from questions.bcba_outline import TOPIC_MAPPING, LETTER_TO_DOMAIN, TOPIC_RELATIONS, TOPICS, SUBDOMAINS
import random

def sample_secondary_domain(main_domain: str):
    """
    Sample a secondary domain to be used for hard questions from the main domain.
    """
    if main_domain not in TOPIC_RELATIONS:
        try:
            main_domain = TOPIC_MAPPING[main_domain]
        except KeyError:
            raise ValueError(f"Domain {main_domain} not found in TOPICS or TOPIC_MAPPING")
    possible_domains = TOPIC_RELATIONS[main_domain]
    if len(possible_domains) == 0:
        return None
    return random.choice(possible_domains)

def sample_subdomains(domain:str, num_subdomains: int = 1):
    """
    Sample a subdomain from the given domains.
    """
    if domain not in TOPICS:
        try:
            domain = LETTER_TO_DOMAIN[domain]
        except KeyError:
            raise ValueError(f"Domain {domain} not found in TOPICS or TOPIC_MAPPING")
    subdomains = list(TOPICS[domain].keys())
    return random.sample(subdomains, num_subdomains)


def get_learning_objectives(main_domain: str, difficulty: str = "medium"):
    main_domain = LETTER_TO_DOMAIN[main_domain]
    result = {
        "domains": [main_domain],
        "subdomains": [],
        "objectives": {}
    }
    if difficulty == "easy":
        subdomains = sample_subdomains(main_domain, 1)
    
    elif difficulty == "medium":
        num_subdomains = random.randint(2, 3)
        subdomains = sample_subdomains(main_domain, num_subdomains)

    elif difficulty == "hard":
        secondary_domain = sample_secondary_domain(main_domain)
        if secondary_domain:
            result["domains"].append(LETTER_TO_DOMAIN[secondary_domain])
            subdomains = [sample_subdomains(domain, 1)[0] for domain in result["domains"]]
        else:
            num_subdomains = random.randint(2, 3)
            subdomains = sample_subdomains(main_domain, num_subdomains)
    result["subdomains"].extend(subdomains)
    result["objectives"].update({subdomain: SUBDOMAINS[subdomain] for subdomain in subdomains})
    return result