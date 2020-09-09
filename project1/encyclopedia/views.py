from django.shortcuts import render, redirect
from django.core.files import File

from random import choice

from . import util
from . import forms


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def article(request, name):
    if name.upper() in (name.upper() for name in util.list_entries()):
        return render(request, "encyclopedia/article.html", {
            "name": name,
            "markdown": util.convert_to_html(util.get_entry(name))
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": 'no such article',
        })


def search(request):
    searched = request.GET['q']
    if searched.upper() in (name.upper() for name in util.list_entries()):
        return redirect("article", name=searched)
    else:
        results = [i for i in util.list_entries() if searched.upper() in i.upper()]
        return render(request, "encyclopedia/search.html", {
            "results": results
        })


def new_page(request):
    if request.method == "POST":
        form = forms.ArticleForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['article_name']
            content = form.cleaned_data['article_content']
            if name.upper() in (x.upper() for x in util.list_entries()):
                return render(request, 'encyclopedia/error.html', {
                    "error": 'article already exist'
                })
            else:
                with open(f'entries/{name}.md', 'w') as f:
                    myfile = File(f)
                    myfile.write(content)
                return redirect("article", name=name)
            return redirect("index")
    else:
        form = forms.ArticleForm()

    return render(request, "encyclopedia/new_page.html", {
        'form': form
    })


def random(request):
    rand = choice(util.list_entries())
    return redirect("article", name=rand)


def edit(request, name):
    if request.method == "POST":
        form = forms.EditForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data['article_content']
        with open(f'entries/{name}.md', 'w') as f:
            myfile = File(f)
            myfile.write(new_content)
        return redirect("article", name=name)
    else:
        existing_content = util.get_entry(name)
        form = forms.EditForm({
            'article_content': existing_content,
        })
        # form.article_name = 'test'
    return render(request, 'encyclopedia/edit.html', {
        'form': form,
        'name': name
    })