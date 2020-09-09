from django import forms


class ArticleForm(forms.Form):
    article_name = forms.CharField(label="Article name", max_length=20)
    #article_name.disabled = True
    article_content = forms.CharField(
        label="Article content",
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 1})
    )


class EditForm(forms.Form):
    article_content = forms.CharField(
        label="Article content",
        widget=forms.Textarea()
    )
