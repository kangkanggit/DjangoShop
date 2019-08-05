#coding:utf-8
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import os
import datetime
from FreshShop.settings import BASE_DIR
class MiddlewareTest(MiddlewareMixin):
    def process_request(self,request):
        """

        :param request: 视图没有处理的请求
        :return:
        """
        username = request.GET.get('username')#获取get请的数据
        # print(username)
        if username and username == '::':#判断请求数据的结果
            return HttpResponse('404')
    def process_view(self,request,view_func,view_args,view_kwargs):
        """

        :param request:视图没有处理的请求
        :param view_func: 视图函数
        :param view_args: 视图函数参数，元组
        :param view_kwargs: 视图函数参数，字典格式
        :return:
        """

        # print(view_func)
    def process_exception(self,request,exception):
        """

        :param request:视图处理请求
        :param exception: 错误
        :return:
        """
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level = 'Error'
        content = str(exception)
        log_result = '%s[%s]%s \n'%(now,level,content)
        file_path = os.path.join(BASE_DIR,'error.log')
        with open(file_path,'a',encoding='utf-8') as f:
            f.write(log_result)
        # print(exception)

    def process_template_response(self,request,response):
         """
                :param request: 视图处理完成的请求
                :param response: 视图处理完成的响应
                """
         # print("这是process_template_response")
         return response

    def process_response(self, request, response):
        """
        :param request: 视图处理完成的请求
        :param response: 视图处理完成的响应
        """
        # print("这是process_response")
        return response