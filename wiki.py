import wikipedia

# Set the language of wikipedia you want to use (default is English)

# Specify the search query

def search(type,search_query):
    if type == 'summary':
        try:
            # Get the summary of the page
            summary = wikipedia.summary(search_query)
            return(f"**Summary of '{search_query}'** \n{summary}\n")

        except wikipedia.exceptions.PageError:
            return(f"'{search_query}' page not found on wikipedia.")

        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            return(f"'{search_query}' may refer to multiple topics. Options:\n{e.options}")
    else:
        try:
            # Get the full text of the page
            full_text = wikipedia.page(search_query).content
            return(f"**Description of '{search_query}'**:\n{full_text}")

        except wikipedia.exceptions.PageError:
            return(f"'{search_query}' page not found on wikipedia.")

        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            return(f"'{search_query}' may refer to multiple topics. Options:\n{e.options}")