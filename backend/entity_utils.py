def normalize_text(text):
    if not isinstance(text, str):
        return text
    return text.strip().lower()

def normalize_entity(entity, fields):
    for f in fields:
        if f in entity:
            entity[f] = normalize_text(entity[f])
    return entity

def deduplicate_entities(entities, key):
    unique = []
    seen = set()
    for e in entities:
        k = e.get(key)
        if k not in seen:
            seen.add(k)
            unique.append(e)
    return unique