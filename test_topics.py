# test_topics.py - Topic detection test

from src.topic_router import detect_topic, has_animation

tests = [
    ('insertion of node in linked list', 'generic'),
    ('binary search tree insertion', 'generic'),
    ('binary search algorithm', 'binary_search'),
    ('bubble sort algorithm', 'bubble_sort'),  
    ('linked list operations', 'generic'),
    ('projectile motion physics', 'projectile_motion'),
    ('sine wave propagation', 'sine_wave'),
    ('quadratic equation solving', 'quadratic'),
    ('stack implementation', 'generic'),
    ('hash table lookup', 'generic'),
    ('pendulum oscillation', 'pendulum'),
    ('explain binary search', 'binary_search'),
    ('bst node deletion', 'generic'),
    ('array insertion at index', 'generic'),
]

print('Topic Detection Test Results:')
print('=' * 60)

passed = 0
failed = 0

for topic, expected in tests:
    result = detect_topic(topic)
    has_anim = has_animation(topic)
    
    if result == expected:
        status = '✅ PASS'
        passed += 1
    else:
        status = '❌ FAIL'
        failed += 1
    
    anim_icon = '🎬' if has_anim else '📄'
    print(f'{status} "{topic}"')
    print(f'       Expected: {expected}, Got: {result} {anim_icon}')

print('=' * 60)
print(f'Results: {passed}/{len(tests)} passed, {failed} failed')
