from django import template

register = template.Library()

@register.simple_tag
def draw_turtle():
    return '''
        <script>
            from turtle import *
            speed(0)
            for i in range(4):
                forward(100)
                right(90)
            done()
        </script>
    '''
