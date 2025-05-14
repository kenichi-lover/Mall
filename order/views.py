from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import json
import os
import sys
from pathlib import Path
from django.utils import timezone 
from django.utils.dateparse import parse_datetime 

from .models import Order, OrderStatus 
from product.models import Product

import logging
logger = logging.getLogger(__name__)

# 初始化阿里支付客户端（最好将其置于单独的工具或服务中）
from alipay import AliPay

def get_alipay_client():
    # 使用 settings 中的配置获取文件路径
    app_private_key_path = settings.ALIPAY_PRIVATE_KEY_FILE
    alipay_public_key_path = settings.ALIPAY_PUBLIC_KEY_FILE

    if not os.path.exists(app_private_key_path):
        logger.error(f"应用私钥文件未找到: {app_private_key_path}")
        raise FileNotFoundError(f"应用私钥文件未找到: {app_private_key_path}")
    if not os.path.exists(alipay_public_key_path):
        logger.error(f"支付宝公钥文件未找到: {alipay_public_key_path}")
        raise FileNotFoundError(f"支付宝公钥文件未找到: {alipay_public_key_path}")

    # 从文件中读取密钥内容
    try:
        app_private_key_string = Path(app_private_key_path).read_text(encoding='utf-8')
        alipay_public_key_string = Path(alipay_public_key_path).read_text(encoding='utf-8')
    except Exception as e:
         logger.error(f"读取支付宝密钥文件失败: {e}")
         raise IOError(f"读取支付宝密钥文件失败: {e}")

    # 初始化 AliPay 客户端，传递密钥内容字符串，使用 settings 中的 APPID 和 debug 模式
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None, # 异步通知URL，根据需要配置 (这里设置为None，在生成支付链接时动态传入)
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2", # 根据你的支付宝配置选择 RSA 或 RSA2
        debug=settings.ALIPAY_DEBUG # 使用 settings 中的 debug 配置
    )
    return alipay

# 在应用启动时初始化客户端，或者在需要时调用 get_alipay_client()
# 为了简化示例，我们仍然在这里初始化，但生产环境建议使用更好的方式管理
try:
    alipay = get_alipay_client()
except (FileNotFoundError, IOError) as e:
    logger.critical(f"支付宝客户端初始化失败: {e}")
    # 根据需要处理初始化失败的情况，例如退出或标记支付功能不可用

@login_required
def buy_now(request, product_id):
    if request.method == 'POST':
        try:
            # 前端发送的是 JSON 格式的数据，所以需要解析 request.body 这个变量。
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            if quantity <= 0:
                return JsonResponse({'status': 'error', 'message': '数量必须大于0'}, status=400)
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.error("无效的请求数据或 JSON 解析失败", exc_info=True)
            return JsonResponse({'status': 'error', 'message': '无效的请求数据'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        # 使用数据库事务来创建订单并减少库存量
        try:
            with transaction.atomic():
                # 使用 select_for_update 锁定行以防高并发问题
                product_in_transaction = Product.objects.select_for_update().get(id=product_id)

                if product_in_transaction.stock < quantity:
                    logger.warning(f"库存不足 Product ID: {product_id}, Requested: {quantity}, Available: {product_in_transaction.stock}")
                    return JsonResponse({'status': 'error', 'message': '库存不足'}, status=400)

                # Create order
                # 在模型的 save 方法中计算并保存 price_at_purchase 和 total_price
                order = Order.objects.create(
                    user=request.user,
                    product=product_in_transaction,
                    quantity=quantity,
                )
                # 该模型的保存方法已经根据“产品价格”和“数量”计算出了“总价”

                # 扣除库存
                product_in_transaction.stock -= quantity
                product_in_transaction.save(update_fields=['stock']) # 仅更新库存字段

            # 返回订单信息，前端应重定向到 payment_page
            logger.info(f"订单创建成功，订单号: {order.order_id}")
            return JsonResponse({'status': 'success', 'order_id': order.order_id, 'message': '订单创建成功'})

        except Exception as e:
            # Log the exception
            logger.error(f"创建订单失败: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': '创建订单失败，请稍后再试'}, status=500)

    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'}, status=405)


@login_required
def payment_page(request, order_id_or_pk):
    """
    显示支付确认页面
    """
    # 假设 order_id 是唯一的字符型字段。
    order = get_object_or_404(Order, order_id=order_id_or_pk, user=request.user)

    if order.status != OrderStatus.UNPAID: # 假设OrderStatus.UNPAID是未支付状态的实际值
        # 如果订单不是待支付状态，重定向到订单详情页或其他合适页面
        if order.status == OrderStatus.PAID: # 假设OrderStatus.PAID是已支付状态的实际值
            logger.info(f"Order {order.order_id} already paid, redirecting to detail page.")
            return redirect(reverse('order:detail', kwargs={'order_id_or_pk': order.order_id})) # 重定向到订单详情页
        elif order.status == OrderStatus.CANCELED: # 假设OrderStatus.CANCELED是已取消状态的实际值
             logger.info(f"Order {order.order_id} is canceled, redirecting to detail page.")
             return redirect(reverse('order:detail', kwargs={'order_id_or_pk': order.order_id})) # 重定向到订单详情页
        else:
             logger.warning(f"Order {order.order_id} in unexpected status {order.status} on payment page.")
             return redirect(reverse('order:detail', kwargs={'order_id_or_pk': order.order_id})) # 重定向到订单详情页

    # 如果订单是待支付状态，渲染支付确认页面
    logger.info(f"Rendering payment confirmation page for order {order.order_id}")
    return render(request, 'order/payment_page.html', {'order': order})


@login_required
def payment_initiate(request, order_id):
    """
    处理支付确认页面的POST请求，生成支付宝支付URL并重定向
    """
    if request.method != 'POST':
         return HttpResponseBadRequest("仅支持POST请求")

    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status != OrderStatus.UNPAID: # 假设OrderStatus.UNPAID是未支付状态的实际值
         logger.warning(f"Attempted to initiate payment for non-unpaid order {order.order_id}, status: {order.status}")
         # 如果订单不是待支付状态，重定向到订单详情页或其他合适页面
         return redirect(reverse('order:detail', args=[order.order_id]))

    # 确保支付宝客户端已成功初始化
    if 'alipay' not in globals() or alipay is None:
        logger.error("Alipay client is not initialized.")
        return render(request, 'order/payment_error.html', {'order': order, 'error_message': '支付系统错误，请联系客服。'})


    # 创建支付请求
    try:
        # 动态生成返回 URL 和通知 URL
        # 请确保您的域名已正确配置（例如，通过 request.get_host() 或 settings 来实现）
        base_url = f"{request.scheme}://{request.get_host()}"
        return_url = base_url + reverse('order:payment_return')
        notify_url = base_url + reverse('order:alipay_notify')

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order.order_id,
            total_amount=str(order.total_price),
            subject=f"订单: {order.product.name} x{order.quantity}",
            return_url=return_url,
            notify_url=notify_url
        )

        # 对于沙盒环境，使用沙箱网关
        pay_url_base = "https://openapi-sandbox.dl.alipaydev.com/gateway.do" if settings.ALIPAY_DEBUG else "https://openapi.alipay.com/gateway.do"
        pay_url = f"{pay_url_base}?{order_string}"

        # **【关键调试步骤】打印生成的 pay_url**
        logger.info(f"Generated pay_url for order {order.order_id}: {pay_url}")

        # 重定向到支付宝支付页面
        return redirect(pay_url)

    except Exception as e:
        # 日志 e
        logger.error(f"生成支付宝 URL 失败，订单号: {order.order_id}: {e}", exc_info=True)
        # 可以在错误页面显示更详细（但不要暴露敏感信息）的错误提示，或者一个错误ID供用户反馈
        return render(request, 'order/payment_error.html', {'order': order, 'error_message': '支付网关通讯失败，请稍后再试或联系客服。'})


@csrf_exempt # 支付宝将在此处直接发送数据，而不会附带 CSRF 令牌。
def alipay_notify_view(request):
    """
    支付宝服务器异步通知处理
    """
    if request.method == 'POST':
        data = request.POST.dict()
        signature = data.pop("sign", None)
        logger.info(f"收到支付宝异步通知，订单号: {data.get('out_trade_no')}")
        # logger.debug(f"Alipay Notify Data: {data}") # 用于详细调试
        # logger.debug(f"Alipay Notify Signature: {signature}") # 用于详细调试

        # 验证签名
        success = alipay.verify(data, signature)

        # 检查 trade_status 和签名是否成功
        if success and data.get("trade_status") in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            order_id = data.get('out_trade_no')
            alipay_trade_no = data.get('trade_no')
            gmt_payment_str = data.get('gmt_payment')

            try:
                with transaction.atomic():
                    # 获取订单，这里不使用 select_for_update 以降低锁竞争，依赖状态检查做幂等
                    order = Order.objects.get(order_id=order_id)
                    logger.info(f"处理订单 {order_id} 的异步通知，当前状态: {order.status}")

                    # 只有在尚未付款的情况下才进行处理（幂等性）
                    if order.status == OrderStatus.UNPAID: # 假设OrderStatus.UNPAID是未支付状态的实际值
                        order.status = OrderStatus.PAID # 假设OrderStatus.PAID是已支付状态的实际值
                        order.transaction_id = alipay_trade_no # 支付宝的交易编号
                        order.payment_method = 'alipay'

                        # 将 gmt_payment 字符串转换为日期时间格式
                        if gmt_payment_str:
                             try:
                                paid_at_datetime = parse_datetime(gmt_payment_str)
                                if paid_at_datetime:
                                     order.paid_at = paid_at_datetime
                                else:
                                     logger.warning(f"无法解析支付宝支付时间字符串: {gmt_payment_str} for order {order_id}")
                                     order.paid_at = timezone.now() # 解析失败时使用当前时间
                             except ValueError:
                                 logger.warning(f"无效的支付宝支付时间字符串格式: {gmt_payment_str} for order {order_id}", exc_info=True)
                                 order.paid_at = timezone.now() # 解析失败时使用当前时间
                        else:
                             order.paid_at = timezone.now() # 如果没有提供支付时间，使用当前时间

                        order.save(update_fields=['status', 'transaction_id', 'payment_method', 'paid_at', 'updated_at']) # 仅更新相关字段

                        # TODO: 在此添加支付后的相关逻辑（例如，发送确认邮件等）
                        logger.info(f"订单 {order_id} 通过异步通知标记为已支付。")
                        return HttpResponse("success") # 告知支付宝处理成功
                    elif order.status == OrderStatus.PAID: # 假设OrderStatus.PAID是已支付状态的实际值
                        logger.info(f"订单 {order_id} 已通过异步通知或其他方式处理（幂等性）。")
                        return HttpResponse("success") # 已经处理完毕，但仍需告知支付宝这是成功的操作。
                    else:
                        logger.warning(f"订单 {order_id} 处于非预期状态 {order.status} 进行异步通知处理。")
                        return HttpResponse("success") # 非待支付状态也视为成功接收通知，避免支付宝重复发送

            except Order.DoesNotExist:
                logger.error(f"支付宝异步通知: 订单 {order_id} 未找到。")
                return HttpResponse("failure") # 订单不存在，告知支付宝失败以便其重试（如果设置了重试）
            except Exception as e:
                logger.error(f"支付宝异步通知: 处理订单 {order_id} 失败: {e}", exc_info=True)
                return HttpResponse("failure") # 告知支付宝出现了问题以便其重试（如果设置了重试）
        else:
            logger.warning(f"支付宝异步通知: 签名验证失败或 trade_status 非成功. Data: {data}, Signature: {signature}")
            return HttpResponse("failure") # 签名或状态有问题，告知支付宝失败

    logger.warning(f"收到非POST请求到支付宝异步通知URL. Method: {request.method}")
    return HttpResponseBadRequest("Invalid request method.")


@login_required
def payment_return_view(request):
    """
    支付宝同步返回处理
    此视图仅用于用户体验，不应作为最终判断支付状态的依据。
    """
    data = request.GET.dict()
    signature = data.pop("sign", None)
    order_id = data.get('out_trade_no')
    alipay_trade_no = data.get('trade_no') # 尝试获取 trade_no
    # gmt_payment_str = data.get('gmt_payment') # 同步返回中可能不包含此字段

    logger.info(f"收到支付宝同步返回，订单号: {order_id}")

    success = alipay.verify(data, signature)

    logger.info(f"Alipay synchronous return verification result: {success}")

    # --- 添加的 DEBUG print 可以保留或暂时移除 ---
    # print(f"--- DEBUG START ---", file=sys.stderr)
    # print(f"DEBUG data dictionary: {data}", file=sys.stderr)
    # print(f"DEBUG data.get('trade_status'): {data.get('trade_status')}", file=sys.stderr)
    # print(f"DEBUG 'trade_status' in data: {'trade_status' in data}", file=sys.stderr)
    # print(f"DEBUG data.get('trade_no'): {data.get('trade_no')}", file=sys.stderr) # 也打印一下 trade_no
    # print(f"--- DEBUG END ---", file=sys.stderr)
    # --- DEBUG print 结束 ---


    # 修改判断条件：签名验证成功 并且 支付宝交易号 (trade_no) 存在
    if success and data.get("trade_no"):

        # --- 成功处理逻辑 ---
        try:
            # 获取订单，并确保订单属于当前用户
            # 注意：这里不依赖同步通知更新订单状态，最终状态以异步通知为准
            order = Order.objects.get(order_id=order_id, user=request.user)
            logger.info(f"同步返回处理成功，订单号: {order_id}，验签成功且包含trade_no。")

            # 虽然同步返回验签并获取到 trade_no，但订单状态的最终更新应依赖异步通知！
            # 可以在这里根据同步返回的数据做一些初步处理或记录，但不要在这里把订单状态强制改成 PAID

            # 您可以在成功页面显示支付宝交易号
            returned_trade_status = data.get('trade_status') # 即使可能为 None，也可以获取并显示
            logger.info(f"同步返回状态（仅供参考）: {returned_trade_status}")

            return render(request, 'order/payment_success.html', {
                'order': order,
                'alipay_return_data': data,
                'alipay_trade_no': data.get('trade_no'), # 传递交易号到模板
                'returned_trade_status': returned_trade_status # 传递同步返回的状态（可能为None）
            })

        except Order.DoesNotExist:
            logger.error(f"支付宝同步返回: 订单 {order_id} 未找到或不属于当前用户。")
            return render(request, 'order/payment_error.html', {'error_message': '订单未找到或权限不足。'})
        except Exception as e:
             logger.error(f"支付宝同步返回: 处理订单 {order_id} 成功块时发生错误: {e}", exc_info=True)
             return render(request, 'order/payment_error.html', {'error_message': '处理同步返回时发生错误。'})

    else:
        # --- 失败处理逻辑 ---
        # 如果验签失败 或 没有trade_no，则视为同步返回失败
        logger.warning(f"支付宝同步返回判断失败. Success: {success}, Data: {data}, Signature: {signature}")

        order = None
        if order_id:
             try:
                 order = Order.objects.get(order_id=order_id, user=request.user)
             except Order.DoesNotExist:
                 pass # 订单不存在也没关系

        return render(request, 'order/payment_failed.html', {'order': order, 'error_message': '支付处理失败或已取消。'})

# 示例：订单详情页面（在付款后或用于查看历史记录时有用）
@login_required
def order_detail_view(request, order_id_or_pk):
    """
    显示订单详情页面
    """
    # 假设 order_id 是唯一的字符型字段
    order = get_object_or_404(Order, order_id=order_id_or_pk, user=request.user)
    logger.info(f"显示订单详情: {order.order_id} for user {request.user.username}")
    return render(request, 'order/detail.html', {'order': order})