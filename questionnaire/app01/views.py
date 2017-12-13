from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from app01 import models


class Foo(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        for item in self.data:
            yield item


def test(request):
    request.POST
    user_list = [
        {'id': 1, 'name': 'alex', 'age': 19},
        {'id': 2, 'name': 'eric', 'age': 18},
    ]
    obj = Foo(user_list)
    return render(request, 'test.html', {'user_list': obj})


from django.forms import ModelForm


class QuestionModelForm(ModelForm):
    class Meta:
        model = models.Question
        fields = ['caption', 'tp']


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields = ['name', 'score']


def question(request, pid):
    """
    问题
    :param request:
    :param pid: 问卷ID
    :return:
    """

    if request.method == "GET":
        def inner():
            que_list = models.Question.objects.filter(naire_id=pid)  # [Question,Question,Question]
            if not que_list:
                # 新创建的问卷，其中还么有创建问题
                form = QuestionModelForm()
                yield {'form': form, 'obj': None, 'option_class': 'hide', 'options': None}
            else:
                # 含问题的问卷
                for que in que_list:
                    form = QuestionModelForm(instance=que)
                    temp = {'form': form, 'obj': que, 'option_class': 'hide', 'options': None}
                    if que.tp == 2:
                        temp['option_class'] = ''

                        # 获取当前问题的所有选项？que
                        def inner_loop(quee):
                            option_list = models.Option.objects.filter(qs=quee)
                            for v in option_list:
                                yield {'form': OptionModelForm(instance=v), 'obj': v}

                        # temp['options'] = inner_loop(que)
                        temp['options'] = inner_loop(que)

                    yield temp

        return render(request, 'que_list.html', {'form_list': inner()})
    else:
        """
        创建问题：
            - pid, 当前问卷ID
            - 数据格式： 
                [
                    {'id':1, 'caption': "鲁宁脸打不打？", 'tp':1},
                    {'id':2, 'caption': "鲁宁脸打不打？", 'tp':2, options:[]},
                ]
        """
        ret = {'status': True, 'msg': None, 'data': None}
        try:
            # 新提交的数据: json.lods(request.body.decode())
            ajax_post_list = [
                {
                    'id': 2,
                    'caption': "鲁宁爱不是番禺？？",
                    'tp': 1,

                },
                {
                    'id': None,
                    'caption': "八级哥肾好不好？",
                    'tp': 3
                },
                {
                    'id': None,
                    'caption': "鲁宁脸打不打？",
                    'tp': 2,
                    "options": [
                        {'id': 1, 'name': '绿', 'score': 10},
                        {'id': 2, 'name': '翠绿', 'score': 8},
                    ]
                },
            ]

            question_list = models.Question.objects.filter(naire_id=pid)

            # 用户提交的所有问题ID
            post_id_list = [i.get('id') for i in ajax_post_list if i.get('id')]

            # 数据库中获取的现在已有的问题ID
            question_id_list = [i.id for i in question_list]

            # 数据库中的那些ID需要删除？
            del_id_list = set(question_id_list).difference(post_id_list)

            # 循环ajax提交过来的所有问题信息
            for item in ajax_post_list:
                # item就是用户提交过来的一个问题
                qid = item.get('id')
                caption = item.get('caption')
                tp = item.get('tp')
                options = item.get('options')

                if qid not in question_id_list:
                    # 要新增
                    new_question_obj = models.Question.objects.create(caption=caption, tp=tp)
                    if tp == 2:
                        for op in options:
                            models.Option.objects.create(qs=new_question_obj, name=op.get('name'),
                                                         score=op.get('score'))

                else:
                    # 要更新
                    models.Question.objects.filter(id=qid).update(caption=caption, tp=tp)

                    if not options:
                        models.Option.objects.filter(qs_id=qid).delete()
                    else:
                        # 不推荐
                        models.Option.objects.filter(qs_id=qid).delete()
                        for op in options:
                            models.Option.objects.create(name=op.get("name"), score=op.get('score'), qs_id=qid)

            models.Question.objects.filter(id__in=del_id_list).delete()
        except Exception as e:
            ret['msg'] = str(e)
            ret['status'] = False
        return JsonResponse(ret)


def student_login(request):
    obj = models.Student.objects.filter(user='龙飞', pwd='123').first()
    request.session['student_info'] = {'id': obj.id, 'user': obj.user}
    return HttpResponse('登录成功')

from django.core.exceptions import ValidationError

def func(val):
    if len(val) < 15:
        raise ValidationError('你太短了')


def score(request, class_id, qn_id):
    """
    :param request:
    :param class_id: 班级ID
    :param qn_id: 问卷ID
    :return:
    """
    student_id = request.session['student_info']['id']
    # 1. 当前登录用户是否是要评论的班级的学生
    ct1 = models.Student.objects.filter(id=student_id, cls_id=class_id).count()
    if not ct1:
        return HttpResponse('你只能评论自己班级的问卷，是不是想转班？')

    # 2. 你是否已经提交过当前问卷答案
    ct2 = models.Answer.objects.filter(stu_id=student_id, question__naire_id=qn_id).count()
    if ct2:
        return HttpResponse('你已经参与过调查，无法再次进行')

    # 3. 展示当前问卷下的所有问题
    # question_list = models.Question.objects.filter(naire_id=qn_id)

    from django.forms import Form
    from django.forms import fields
    from django.forms import widgets

    # # 类：方式一
    # class TestForm(Form):
    #     tp1 = fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #     tp2 = fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #     tp3 = fields.CharField(label='对路宁的建议？',widget=widgets.Textarea)
    #     tp4 = fields.ChoiceField(label='路宁帽子颜色？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #
    # # 类：方式二
    # MyTestForm = type("MyTestForm",(Form,),{
    #     'tp1': fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    #     'tp2': fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    #     'tp3': fields.CharField(label='对路宁的建议？',widget=widgets.Textarea),
    #     'tp4': fields.ChoiceField(label='路宁帽子颜色？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    # })
    # return render(request,'score.html',{'question_list':question_list,'form':MyTestForm()})
    question_list = models.Question.objects.filter(naire_id=qn_id)
    field_dict = {}
    for que in question_list:
        if que.tp == 1:
            field_dict['val_%s' % que.id] = fields.ChoiceField(
                label=que.caption,
                error_messages={'required':'必填'},
                widget=widgets.RadioSelect,
                choices=[(i, i) for i in range(1, 11)]
            )
        elif que.tp == 2:
            field_dict['option_id_%s' % que.id] = fields.ChoiceField(
                label=que.caption,
                widget=widgets.RadioSelect,
                choices=models.Option.objects.filter(
                    qs_id=que.id).values_list('id', 'name'))
        else:
            from django.core.exceptions import ValidationError
            from django.core.validators import RegexValidator
            # field_dict['x_%s' % que.id] = fields.CharField(
            #     label=que.caption, widget=widgets.Textarea,validators=[RegexValidator(regex=""),])
            field_dict['content_%s' % que.id] = fields.CharField(
                label=que.caption, widget=widgets.Textarea, validators=[func, ])
    # 类：方式二
    MyTestForm = type("MyTestForm", (Form,), field_dict)

    if request.method == 'GET':
        form = MyTestForm()
        return render(request, 'score.html', {'question_list': question_list, 'form': form})
    else:
        # 15字验证
        # 不允许为空
        form = MyTestForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            # {'x_2': '3', 'x_9': 'sdfasdfasdfasdfasdfasdfasdf', 'x_10': '13'}
            objs = []
            for key,v in form.cleaned_data.items():
                k,qid = key.rsplit('_',1)
                answer_dict = {'stu_id':student_id,'question_id':qid,k:v}
                objs.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(objs)
            return HttpResponse('感谢您的参与!!!')

        return render(request, 'score.html', {'question_list': question_list, 'form': form})
