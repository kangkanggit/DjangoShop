from rest_framework.renderers import JSONRenderer

class Customrenderer(JSONRenderer):
    def render(self,data,accepted_media_type=None,renderer_context = None):
        """

        :param data: 返回的数据
        :param accepted_media_type:接收的类型
        :param renderer_context: 展示的内容
        :return:
        """
        if renderer_context:#判断是否有数据请求过来
            if isinstance(data,dict):
                msg = data.pop('msg','请求成功')
                code = data.pop('code',0)
            else:
                msg = '请求成功'
                code = 0
            ret = {
                'msg':msg,
                'code':code,
                'author':'最帅的康哥',
                'data':data
            }
            return super().render(ret,accepted_media_type,renderer_context)
        else:
            return super().render(data,accepted_media_type,renderer_context)