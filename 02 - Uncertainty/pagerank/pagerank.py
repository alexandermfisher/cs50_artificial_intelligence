import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    if corpus[page]:
        distribution_dict = dict(zip(corpus.keys(), [(1 - damping_factor) / len(corpus)] * len(corpus)))
        for link in corpus[page]:
            distribution_dict[link] += damping_factor / len(corpus[page])
        return distribution_dict
    else:
        distribution_dict = dict(zip(corpus.keys(), [1 / len(corpus)] * len(corpus)))
        return distribution_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # initialise page ranks dict. I.e. All keys start off on count of 0.
    page_ranks = dict(zip(corpus.keys(),[0]*len(corpus)))

    # initialise iterative process by selecting a random page to begin on and addding 1 to count for that page.
    # then complete remaining samples. 
    current_page = random.choice(list(corpus.keys()))
    page_ranks[current_page] += 1 
    count = 1
    while count != n:
        distribution = transition_model(corpus,current_page,damping_factor)
        current_page = random.choices(list(distribution.keys()),list(distribution.values()))[0]
        page_ranks[current_page] += 1
        count += 1
    
    # normalise page_rank values by dividing by n.
    for key in page_ranks:
        page_ranks[key] /= n    

    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = dict(zip(corpus.keys(), [1/len(corpus)] * len(corpus)))
    differences = dict(zip(corpus.keys(), [100] * len(corpus)))

    # if a page (in coprus) contains no links then add a link to every page in corpus. 
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = corpus.keys()

    # loop through updating page ranks according to formula until difference below 0.001 (error tolerance).
    error_tol = 0.0001
    keep_in_loop = True
    while keep_in_loop:
        for page in page_ranks:
            updated_page_rank = ((1-damping_factor)/len(corpus)) + (damping_factor * to_page_prob(page, corpus, page_ranks))
            differences[page] = abs(page_ranks[page] - updated_page_rank)
            page_ranks[page] = updated_page_rank

        if all(difference < error_tol for difference in differences.values()):
            keep_in_loop = False
    
    return page_ranks

def to_page_prob(page_p,corpus,page_ranks):
    """ Returns probability of getting to page_p from 
    all other links. I.e. the second part of the PageRank Fomula.
    """
    probability = 0
    for page_i in page_ranks:
        if page_p in corpus[page_i]:
                    probability += page_ranks[page_i]/len(corpus[page_i])
    return probability
            



if __name__ == "__main__":
    main()
