from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Renderiza o template home.html



def search_results_view(request):
    query = request.GET.get('q')
    # Lógica de busca aqui
    return render(request, 'core/search_results.html', {'query': query})
