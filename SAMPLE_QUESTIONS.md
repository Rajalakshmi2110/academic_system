# CA3101 Sample Questions - All Units & Validation Types

## Legend
- VALID: Passes all layers, gets answer (may include corrections)
- WARNING: In syllabus but poor quality
- REJECTED: Gibberish or critical incorrect facts (hardcoded in Layer 2)
- OUT_OF_SYLLABUS: Not DS-related OR DS but not in CA3101

## Unit 1: Introduction
VALID: "What is Big O notation?"
WARNING: "Tell me everything about data structures"
REJECTED: "asdfghjkl"
OUT_OF_SYLLABUS: "What is AWS S3?"

## Unit 2: Arrays & Linked Lists
VALID: "What is the difference between arrays and linked lists?"
VALID: "Explain doubly linked list"
VALID: "Linked list search is O(1)" (Layer 3 corrects to O(n))
WARNING: "Which is better array or linked list?"
REJECTED: "qwertyuiop"
OUT_OF_SYLLABUS: "What is a rope data structure?"

## Unit 3: Stacks & Queues
VALID: "What is a stack and its operations?"
VALID: "Explain priority queue"
WARNING: "What is the best queue implementation?"
REJECTED: "Stack is FIFO" (hardcoded rule catches this)
REJECTED: "Queue is LIFO" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is Kafka queue?"

## Unit 4: Trees
VALID: "What is AVL tree rotation?"
VALID: "Explain binary search tree"
VALID: "What is a B-tree?"
WARNING: "Which tree is best?"
REJECTED: "Trees have cycles" (hardcoded rule catches this)
REJECTED: "Binary search is O(n^2)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is a red-black tree?"

## Unit 5: Graphs
VALID: "Explain BFS algorithm"
VALID: "What is Dijkstra algorithm?"
VALID: "Explain Kruskal algorithm"
VALID: "Dijkstra is O(n^3)" (Layer 3 corrects complexity)
WARNING: "Which graph algorithm is best?"
REJECTED: "asdfasdf"
OUT_OF_SYLLABUS: "What is GraphQL?"

## Unit 6: Heaps
VALID: "What is a heap data structure?"
VALID: "Explain min-heap and max-heap"
VALID: "Heap sort is O(n)" (Layer 3 corrects to O(n log n))
WARNING: "Which heap is better?"
REJECTED: "tyuityui"
OUT_OF_SYLLABUS: "What is a Fibonacci heap?"

## Unit 7: Hashing
VALID: "What is hashing and hash function?"
VALID: "Explain collision resolution"
VALID: "What is linear probing?"
VALID: "Hashing is O(n^2)" (Layer 3 corrects to O(1) average)
WARNING: "Which hashing technique is best?"
REJECTED: "fghjfghj"
OUT_OF_SYLLABUS: "What is a bloom filter?"

## Unit 8: Sorting
VALID: "What is bubble sort?"
VALID: "Explain quicksort algorithm"
VALID: "What is merge sort?"
VALID: "Quicksort is O(n^3)" (Layer 3 corrects to O(n log n))
WARNING: "Which sorting is best?"
REJECTED: "Bubble sort is O(n log n)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "How to use Arrays.sort() in Java?"

## Unit 9: Searching
VALID: "What is binary search?"
VALID: "Explain linear search"
VALID: "Linear search is O(1)" (Layer 3 corrects to O(n))
WARNING: "Which search is best?"
REJECTED: "Binary search is O(n)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is Elasticsearch?"

## Unit 10: Recursion
VALID: "What is recursion?"
VALID: "Explain Tower of Hanoi"
WARNING: "Is recursion better than iteration?"
REJECTED: "poiupoiu"
OUT_OF_SYLLABUS: "What is tail call optimization?"

## Notes on Incorrect Facts Handling

### Rejected by Layer 2 (8 hardcoded patterns):
1. "Binary search is O(n^2)" or O(n^3) or O(n)
2. "Stack is FIFO"
3. "Queue is LIFO"
4. "Trees have cycles"
5. "Linked list search is O(1)"
6. "Bubble sort is O(n log n)"

### Corrected by Layer 3 (Educational approach):
- "Heap sort is O(n)" → Corrects to O(n log n)
- "Quicksort is O(n^3)" → Corrects to O(n log n)
- "Hashing is O(n^2)" → Corrects to O(1) average
- "Dijkstra is O(n^3)" → Corrects to O(V^2) or O(E log V)
- "Linear search is O(1)" → Corrects to O(n)
- And many other incorrect complexity claims

This hybrid approach:
- Catches critical conceptual errors (LIFO/FIFO, cycles in trees)
- Lets LLM educate students on complexity mistakes
- Provides flexibility without maintaining 100+ hardcoded rules



Sample Questions to Test Your MCP System
:white_check_mark: VALID Questions (Should get answers)
Basic Concepts:
1. What is a stack?
2. Explain linked list
3. How does BFS work?
4. What is time complexity?
5. Difference between stack and queue
With Typos (Tests MCP leniency):
6. explain dijkstra algoritm
7. what is binery search
8. how to travers a tree
9. explain quik sort
10. what is haep data structure
Broad Questions:
11. Explain sorting algorithms
12. What are tree traversal methods?
13. Tell me about graph algorithms
14. Explain hashing techniques
15. What are different types of trees?
Short Questions:
16. AVL tree?
17. DFS vs BFS
18. Big O notation
19. Recursion
20. Hash collision
Complex Questions:
21. How does Dijkstra's algorithm find shortest path?
22. What is the time complexity of quicksort in worst case?
23. Explain AVL tree rotations with example
24. How does chaining handle hash collisions?
25. What is the difference between 2-3 tree and B-tree?

:x: OUT_OF_SYLLABUS Questions (Should be rejected)
Advanced DS (Not in CA3101):
26. Explain skip list
27. What is fibonacci heap?
28. How does red-black tree work?
29. Tell me about splay trees
30. Explain segment tree
Non-DS Topics:
31. How to deploy on AWS?
32. What is React hooks?
33. Explain SQL joins
34. How does Docker work?
35. What is MongoDB?

:x: REJECTED Questions (Gibberish)
36. asdfasdf
37. ????????
38. qwertyuiop
39. jkjkjkjkjk
40. 12345678

:dart: Edge Cases (Tests MCP intelligence)
Incorrect Facts (Should still get answer with correction):
41. Is binary search O(n^2)?
42. Stack is FIFO right?
43. Queue is LIFO correct?
44. Trees can have cycles?
45. Linked list search is O(1)?
Very Short:
46. BFS
47. Stack
48. Array
49. Graph
50. Heap