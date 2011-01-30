mapping = {}
for obj in 'generic.Text generic.TextArea generic.ListPage tasks.TasksPage tasks.Task markdown.MarkdownPage'.split():
    namespace, klass = obj.rsplit('.', 1)
    mapping['flaskbox.objects.%s %s'%(namespace, klass)] = 'drink.objects.%s %s'%(namespace, klass)

