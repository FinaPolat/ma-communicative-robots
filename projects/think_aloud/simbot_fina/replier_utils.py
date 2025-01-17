from itertools import combinations
import random

#### The writer of this function is Thomas Belluci. It has been slightly modified for Simbot by Fina Polat. ####

def thoughts_from_brain(brain_response):
    """ Takes a brain response capsule and extracts the thoughts from it.

        params
        dict capsule: dict containing the input utterance, triples, perspectives
                      and contextual information (e.g. location, speaker)
        object typer: Typing object that maps a token to a type (a hypernym).

        returns:      dict mapping from thought names to (thought_type, thought_info)
    """
    utt = brain_response['statement']
    cap = brain_response['thoughts']

    ## Trust is always available
    thoughts = dict()
    thoughts['_trust'] = ('_trust', cap['_trust'])

    ## Any statement novelties? (can always be called!)
    if cap['_statement_novelty']:  # == previous claims!
        thoughts['no_statement_novelty'] = ('_statement_novelty', cap['_statement_novelty'])
    else:
        thoughts['statement_novelty'] = ('_statement_novelty', cap['_statement_novelty'])

    ## Any single overlap, e.g. 'overlap animal'
    for overlap in cap['_overlaps']['_subject']:
        overlap_name = 'overlap %s' % overlap['_entity']['_types'][-1]
        thoughts[overlap_name] = ('_overlaps', {'_subject': [overlap], '_complement': []})

    for overlap in cap['_overlaps']['_complement']:
        overlap_name = 'overlap %s' % overlap['_entity']['_types'][-1]
        thoughts[overlap_name] = ('_overlaps', {'_subject': [], '_complement': [overlap]})

    ## Any pairs of overlaps, e.g. 'overlap animal person'
    for overlaps in combinations(cap['_overlaps']['_subject'], r=2):
        entities = sorted([overlaps[0]['_entity']['_types'][-1],
                           overlaps[1]['_entity']['_types'][-1]])
        overlap_name = 'overlap %s %s' % (entities[0], entities[1])
        thoughts[overlap_name] = ('_overlaps', {'_subject': overlaps, '_complement': []})

    for overlaps in combinations(cap['_overlaps']['_complement'], r=2):
        entities = sorted([overlaps[0]['_entity']['_types'][-1],
                           overlaps[1]['_entity']['_types'][-1]])
        overlap_name = 'overlap %s %s' % (entities[0], entities[1])
        thoughts[overlap_name] = ('_overlaps', {'_subject': [], '_complement': overlaps})

    ## Any entity novelties?
    if cap['_entity_novelty']['_subject']:
        novelty_name = 'entity_novelty %s' % utt['triple']['_subject']['_types'][0]
        novelty_info = {'_subject': True, '_complement': False}
        thoughts[novelty_name] = ('_entity_novelty', novelty_info)

    if cap['_entity_novelty']['_complement']:
        novelty_name = 'entity_novelty %s' % utt['triple']['_complement']['_types'][0]
        novelty_info = {'_subject': False, '_complement': True}
        thoughts[novelty_name] = ('_entity_novelty', novelty_info)

    ## Any subject gaps?, e.g. 'subject_gap person animal'
    for gap in cap['_subject_gaps']['_subject']:
        gap_name = 'subject_gap %s %s' % (utt['triple']['_subject']['_types'][0],
                                          gap['_entity']['_types'][-1])
        thoughts[gap_name] = ('_subject_gaps', {'_subject': [gap], '_complement': []})

    for gap in cap['_subject_gaps']['_complement']:
        gap_name = 'subject_gap %s %s' % (utt['triple']['_subject']['_types'][0],
                                          gap['_entity']['_types'][-1])
        thoughts[gap_name] = ('_subject_gaps', {'_subject': [], '_complement': [gap]})

    ## any object gaps?, e.g. 'object_gap person animal'
    for gap in cap['_complement_gaps']['_subject']:
        gap_name = 'object_gap %s %s' % (utt['triple']['_complement']['_types'][0],
                                         gap['_entity']['_types'][-1])
        thoughts[gap_name] = ('_complement_gaps', {'_subject': [gap], '_complement': []})

    for gap in cap['_complement_gaps']['_complement']:
        gap_name = 'object_gap %s %s' % (utt['triple']['_complement']['_types'][0],
                                         gap['_entity']['_types'][-1])
        thoughts[gap_name] = ('_complement_gaps', {'_subject': [], '_complement': [gap]})

    ## Any complement conflicts (cardinality conflict)?
    if cap['_complement_conflict']:
        thoughts['complement_conflict'] = ('_complement_conflict', cap['_complement_conflict'][:1])  # Nothing

    ## A negation conflict?
    positives = [item for item in cap['_negation_conflicts'] if item['_polarity_value'] == 'POSITIVE']
    negatives = [item for item in cap['_negation_conflicts'] if item['_polarity_value'] == 'NEGATIVE']

    if positives and negatives:
        conflict_info = [random.choice(positives), random.choice(negatives)]  # Nothing
        thoughts['negation_conflict'] = ('_negation_conflicts', conflict_info)

    # Scramble to break ordering!
    thoughts = list(thoughts.items())
    random.shuffle(thoughts)
    return dict(thoughts)
