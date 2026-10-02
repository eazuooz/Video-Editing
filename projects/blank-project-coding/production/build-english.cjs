const fs=require('node:fs'),path=require('node:path');
const ko=JSON.parse(fs.readFileSync(path.join(__dirname,'../script/narration.ko.json'),'utf8'));
const rows=[
['After the Tutorial, Why Can’t I Start Alone?',[
'You followed a Tetris tutorial to the end. Blocks fall, rotate, and disappear when a line fills. You typed the code yourself.',
'But what happens when you close the project and the tutorial, then open a new, empty project? You may get stuck on the first line. Where should I begin?',
'Today we will explore that gap: practicing the move from understanding code when you see it to starting a program yourself from nothing.',
'Even one moving block connects input, position, collision, and state changes. As we build, think about who decided how those actions should happen and in what order.'
]],
['Freshmen and Sophomores: Start from Scratch',[
'I especially want to emphasize this to first- and second-year computer science students.',
'While learning programming, turn off AI and, when possible, start a program from scratch without looking at the answer code.',
'The important question is what we mean by making it yourself. Did your hands enter decisions made by someone else, or did you decide how to solve the problem?'
]],
['Following Examples Also Has a Purpose',[
'Typing a book example, reproducing an instructor’s function, and reading other people’s code all have a place. When you are new, you may not even know where to begin.',
'Here we read an existing node definition and insertion code. We find the variable that points to the next node, then run the program to check the connections.',
'This is time for learning the concept, and reading good code helps. Understanding this example alone does not yet establish that you can design the same feature yourself.',
'Pause execution and follow the next pointer. Check which actual values those names refer to. After observing the principle, practice retrieving and using it on your own.'
]],
['Separate Understanding from Independent Implementation',[
'I am not recommending that you abandon books and tutorials. Learn from them first, then set aside time to close the answer and rebuild.',
'With the answer beside you, the next line is already visible. Starting from scratch requires you to decide which data you need and how to process it before writing that line.',
'You do not need to memorize every language feature from the start. Choose a small feature you have learned and see how far you can think through and implement it without help.'
]],
['After Studying Linked Lists, Close the Answer',[
'Suppose you have studied linked lists: what a node is, how a pointer refers to the next node, and how insertion and deletion work.',
'Now close the example and the tutorial. Temporarily turn off AI completion. Prepare your development environment and open a new project with an empty main function.',
'Try implementing the linked list yourself. You might get stuck at how to declare a node. That is fine. You are finding where your independent implementation stops.',
'Pause searches for the answer and write down the values a node needs. What should head contain before the first node exists? Decide the starting state of the empty list yourself.'
]],
['Decide What You Need Before the First Line',[
'If you cannot write code yet, describe what you need. A node stores a value. A connection leads to the next node. A head pointer identifies the beginning.',
'Start with a small goal: connect two nodes and print their values from the front. You do not have to finish insertion, deletion, and every edge case at once.',
'That divides the goal into declaring nodes, linking them, and traversing them. When the first line will not come to mind, decide the first thing the program must do.'
]],
['Create and Connect Two Nodes',[
'In the editor, we create nodes containing ten and twenty. Typing speed is not the point; deciding what to store and where is.',
'Make the first node point to the second and leave the final next pointer empty. Start at head and follow each connection while printing the values.',
'Look at the actual output: does ten come before twenty? Thinking that the nodes are connected and checking that the code connects them are separate steps.',
'Also check that traversal stops at the final empty connection. Confirm both the two printed values and the stopping condition before adding another feature.'
]],
['What Must Change to Insert a Node?',[
'Now we want to insert fifteen between ten and twenty. Creating a node alone does not put it into the list. The connections must change too.',
'First set the new node’s next pointer so we do not lose the existing twenty. Then make the preceding node point to the new node.',
'Instead of memorizing the finished code, explain which connection to change first so the remaining nodes stay reachable. Translate that explanation into code.'
]],
['Inspect the Connections After Insertion',[
'Back in the editor, implement insertion in the order we chose. Run it and check that the values appear as ten, fifteen, twenty.',
'If the output stops at fifteen and twenty disappears, what should you suspect? Check whether you lost the original next connection, rather than only checking that the new node exists.',
'Pause at a breakpoint and inspect the next pointers of the preceding and new nodes. Compare what they point to before and after insertion. These changes correspond to the arrows we just saw.',
'Once twenty remains reachable, insert another node. Check that the order survives a different value. Do not finish verification after a single successful output.'
]],
['Decide Deletion and Edge Cases Yourself',[
'Delete the middle node. Make its predecessor point to the following node, then release the node you no longer use. Check that you never follow the deleted node again.',
'After middle deletion works, remove the first node. What should head point to? If the only node is deleted, how will you represent an empty list?',
'Call the function on an empty list too. If execution fails or accesses invalid memory, trace the missing condition. Change the inputs to check whether your rules actually work.',
'After freeing a node, do not read its value again. Preserve the connection you need before deletion and traverse only the surviving list. Observe the order of connection changes and cleanup in execution.'
]],
['A Sticking Point Shows What to Study Next',[
'If declaring a node stops you, revisit how to represent data. If insertion order stops you, revisit connections. For deletion, examine lifetime and boundary conditions.',
'Forgetting some code does not mean all your study was wasted. Independent implementation reveals more precisely what you understand and where you need help.',
'After reviewing the concept, close the material and implement it again. Check whether you can explain why each line is needed, rather than how many lines you memorized.'
]],
['After the Tetris Tutorial, Open a New Project',[
'Tetris works the same way. The instructor builds the board and blocks, implements collision and rotation, and adds line clearing. Following along produces a running game.',
'Now try once more. Preserve and close the finished project. Turn off the tutorial and stop looking at its source. Open a new, empty project.',
'The questions change: where should block data live? Should the board be a two-dimensional array? When should collision be checked? This time you must answer, rather than the instructor.',
'Decide the first small version you can run. Before scores and previews, display one block on the board. Start writing the necessary data in the new file and work toward that first execution.'
]],
['Do Not Build All of Tetris at Once',[
'You do not have to pour out code for a complete Tetris game immediately. Divide the work into displaying the board and block, movement, collision, rotation, locking, and line clearing.',
'Today, showing one block and moving it one cell right can be enough. Confirm that behavior, then prevent it from crossing the wall.',
'Breaking up work and choosing its order are also programming practice. Before naming functions and classes, decide which small result you can verify now.'
]],
['Connect Board Data, a Block, and One Input',[
'In the development view, first display an empty board. Keep the block shape separate from its current position and draw a four-cell block.',
'Connect the right-arrow input and move it one cell. Watch not only the block but also how its coordinates change after the input.',
'The displayed block begins to connect with the stored data. Instead of waiting for the instructor’s next line, you decide which value must change to create the behavior.',
'Draw the same shape elsewhere. If shape data and board position are separate, you can change position without rewriting the shape. Check which tasks your representation makes easier.'
]],
['Check a Candidate Position Before Moving',[
'Changing the current position unconditionally on a right-arrow press lets the block cross a wall. Instead, first construct a candidate one cell to the right and check it.',
'Check whether any occupied cell would leave the board or overlap an existing cell. Commit the position only when it is valid.',
'The goal is not to memorize the correct move function. Build the decision sequence yourself: receive input, form a candidate, check it, and apply it if allowed.'
]],
['Press the Keys at Walls and Occupied Cells',[
'After writing the code, do not test only the middle. Move to the right wall and press right again, then try the same input next to existing blocks.',
'At a blocked position, verify that the coordinates remain unchanged. Even if the picture looks stationary, changed internal values can break the next action.',
'Compare movement in empty space with staying still when blocked. You are checking whether the actual input results match the rule you described.',
'Now move downward. Can the same check work on that candidate position? Try another direction and confirm that it stops above the floor and occupied cells to see how far the rule applies.'
]],
['Rotation Is Another Decision',[
'Rotation raises more questions. How should the shape be represented? How do we calculate the rotated cells? What if the new shape overlaps a wall or another block?',
'For an initial exercise, choose a simple rule: check the rotated candidate and keep the original shape if it cannot be placed.',
'You do not need every adjustment used by commercial Tetris rotation systems immediately. Begin by implementing and explaining your own small rule accurately.'
]],
['Does Rotation Work Beside a Wall?',[
'Connect the function that constructs and checks a rotation candidate. Rotate once in the middle, then press the same key beside a wall and existing blocks.',
'Check that an invalid rotation is rejected while the original shape and position remain. Only a successful check should change the shape.',
'If a bug appears, inspect the candidate result and commit order before replacing the entire rotation formula. Separate a calculation error from changing state despite a failed check.',
'Try another shape at the same position. Is a rotation rejected when even one of its four cells leaves the board? Checking only the origin can differ from checking every occupied cell.'
]],
['Line Clearing Reveals Why Order Matters',[
'When a block cannot descend, lock it into the board, find full rows, remove them, and move the remaining rows down. One visible action contains that sequence.',
'Instead of filling only one row, prepare a board that completes two adjacent rows. Check that removing one does not cause the next to be skipped.',
'Decide which rows should remain and compare that expectation with the result. Go beyond saying the game ran once: record which conditions you checked.',
'Leave a single block above the rows to be cleared and watch where it moves afterward. Verify that the surviving data reaches the position used by the next turn, not merely that the clearing effect plays.'
]],
['Reading Code and Producing Code Are Different',[
'Reading AI output or a book example and understanding how it works is useful. Reading the structures other developers choose matters too.',
'But reading alone mainly exercises recognizing something in front of you. Recognition is a useful term for describing this distinction.',
'With an empty project, no answer is visible. Alongside recall, you need problem solving: dividing the task and choosing data structures, functions, and implementation order.',
'Reading code can involve deep thought too. The point is to check comprehension and independent design and implementation separately.'
]],
['Can You Apply the Principle Beyond Memorized Code?',[
'When rebuilding, try changing one condition. If you implemented insertion at the front of a linked list, try appending to the end.',
'Here we insert the first node into an empty list, then append to a nonempty list. Decide how to handle head and the final connection in each case.',
'Memorizing the old sequence of lines may leave you stuck again. Understanding the connections lets you explain and adapt the required operations.',
'Front insertion changed head to the new node. Which connection changes for tail insertion? Traverse to the final node, attach a new value, and print the whole order again.'
]],
['Think About Speaking a Foreign Language',[
'Suppose you have read a thousand English sentences and can understand them. Close the book and try expressing your own thoughts aloud; suddenly nothing may come out.',
'You need time both to understand what you see and to build sentences yourself. I think programming is similar.',
'Reading linked-list code ten times is different from closing the answer and implementing it yourself. Understanding Tetris code and choosing its structure in an empty project are different too.',
'Look at resources while learning. Read books, watch tutorials, and ask AI to explain concepts. Once you understand enough, close them and spend time making the program yourself.'
]],
['Translate Your Own Explanation into a Function',[
'This time, describe the work briefly instead of reading a completed function: find full rows, decide what to remove, and gather the remaining rows at the bottom.',
'Build a small function in that order, then run both a one-row and a two-row case. Pay attention to the input and the expected result together.',
'Focus on whether your chosen processing order produces the result, rather than typing the same code repeatedly. An idea you could explain becomes conditions and iteration in code.',
'Hide the function’s name and explain what input it receives and what result it produces. Check whether you understand the process or merely recognize the name, then try another input.'
]],
['Getting Stuck Is Part of Studying',[
'Starting from scratch naturally involves getting stuck. You may forget a node declaration, confuse pointers, or wonder how to check collisions.',
'A problem that an answer solves in ten seconds may take thirty minutes of thought, or a bug may take two hours. I believe that process can contain important practice.',
'Form an expectation, run the program, set a breakpoint, inspect variables, and correct your assumptions. Time spent stuck is not itself the goal; what you checked and changed matters.'
]],
['Trace a Wall-Crossing Bug at a Breakpoint',[
'Reproduce the block crossing the wall. Before changing random code, state the expectation: pressing right at the right wall should leave its position unchanged.',
'Pause movement processing and inspect candidate coordinates, board width, and the collision result. Follow which cells are checked and when the position is committed.',
'A bug can exist without an error message. Running successfully and following the intended rule are different. Find where the expectation first diverges from the result.',
'Do not change several functions at once. Follow the values after this input reaches movement processing. Compare the current position before and after the check to distinguish forming a candidate from already changing the state.'
]],
['Change One Hypothesis and Retry the Same Input',[
'If the code changes position before checking collision, suspect the order. Modify it to check the candidate first and commit only on success.',
'Press the same key beside the wall where the problem occurred. Confirm that position remains unchanged, and that movement still works in the empty center. Check that the fix did not block valid movement.',
'Write one sentence explaining the cause: the current coordinate changed despite a failed check. That record gives you a starting point for the next investigation.',
'Test the opposite wall too. Check whether the movement condition holds on both sides, rather than only whether the right-wall symptom disappeared. Record the inputs you retried alongside the fix.'
]],
['Take a Focused Hint, Then Close the Answer Again',[
'Thinking independently does not mean refusing help forever. If you keep circling the same problem, summarize the expected result, actual result, and what you have already checked.',
'Ask a teacher or colleague, or consult the needed documentation and concept explanation. With AI, you can request a hint about the next condition to inspect instead of the entire solution.',
'Once you understand the hint, close it and implement the idea. Explain why the change was needed and try applying it under similar conditions. Keep responsibility for the thinking.'
]],
['Ask a Specific Question and Rebuild Without the Answer',[
'If two rows should disappear but only one does, record that input and result before asking for the whole Tetris game to be rewritten. Note how the row being checked changes during iteration.',
'After reviewing the concept, close the material and rewrite the small row-compaction function. Test both adjacent and separated full rows.',
'Even after receiving help, make the decisions, implement, and verify yourself. Go beyond understanding the hint and check whether the principle handles a changed input.',
'Record the missed condition: deleting a row changed what would be checked next. Next time, decide which rows remain and where they move first. Turn the help into questions for your next implementation.'
]],
['Why I Recommend Different AI Use as Skills Develop',[
'That is why I recommend plenty of this practice in your first two years. After studying a data structure, close the answer and implement it. After studying an algorithm, close the explanation and solve it again.',
'After a game programming tutorial, rebuild a small feature in an empty project. Before asking AI for finished code, take time to break up the problem yourself.',
'As basic proficiency develops and projects grow in later years, use AI to improve productivity: repetitive code, library research, test ideas, and refactoring.',
'Your year at university does not automatically determine your skill. Expand tool use based on whether you can choose the structure, verify results, and investigate problems.'
]],
['Use AI After You Have Chosen the Structure',[
'Once you can explain the basic structure, you can ask AI for repetitive setup code or draft tests. Decide the inputs and expected results yourself first.',
'In the development view, read what the added code changes, then retry an empty board, a wall, and a two-row clear. Receiving a suggestion does not complete verification.',
'AI can then help implement work you have defined more quickly. If a result differs from your expectation, inspect the program’s state and judge it yourself.',
'Passing tests does not replace checking the screen. Use actual inputs to move and rotate, and examine whether the changed function affects other behavior. Decide what to delegate and what to verify.'
]],
['The Goal Is to Think While Using Tools',[
'My message is not that you should avoid AI. While learning programming, do not outsource the thinking process itself.',
'At work, we consult documentation, read existing code, search, use AI, and ask colleagues. What matters is retaining the ability to turn a problem into a program while using those tools.',
'Tools can be efficient when the goal is finishing an assignment quickly. When the goal is learning, I hope you will judge more than how fast the final result appeared.'
]],
['Choose Your Own Order for Another Small Game',[
'Now transfer the exercise to a small brick-breaker game. Display a ball and paddle, move the paddle with input, and decide which values change when the ball touches it.',
'Do not simply paste Tetris code. Identify this game’s state and collision conditions, then implement and run one behavior at a time.',
'Apply a learned principle to a new problem. You may be slow and get stuck at first. With practice, you begin to see what to store and in what order to process it.',
'Test hits at the paddle’s center and edge. Write the expected response and compare it with the actual ball movement. Even in another game, narrowing problems by comparing predictions with execution remains useful.'
]],
['Bring Your Sticking Point to YamyamCoding Coaching',[
'Practicing alone can leave you unsure where to begin or what to change in your code. Questions that organize your thoughts and feedback on your code can help.',
'If you want to develop a habit of designing and implementing programs yourself, explore YamyamCoding programming coaching and tutoring. The information is for learners seeking direction in breaking down and implementing game programming problems.',
'The coaching and tutoring link will be in the description, at the end of the video, and in the pinned comment. Summarize what you are learning, the code you have made, and where you are stuck. Begin with a specific account of the help you need.'
]],
['Open an Empty Project Today',[
'Choose just one small feature you have learned. Close the book and tutorial, temporarily turn off AI, and open an empty project.',
'Start from nothing yourself. Your first attempt does not have to succeed. Find where you get stuck, learn what you need, and try making it again.',
'After building your ability to decide and implement independently, use AI again as a tool that helps realize your own ideas much faster.',
'Today’s first goal can be small: put a value into an empty list and take it out, or move and stop one object on screen. This time, choose that small beginning yourself.'
]]
];
if(rows.length!==ko.scenes.length)throw Error('Scene mismatch');
const result={title:'CS Freshmen and Sophomores: Close the Tutorial and Start from Scratch',language:'en',translationBasis:'Faithful paragraph-aligned translation of approved Korean revision; timings use measured Korean speech.',scenes:ko.scenes.map((s,i)=>{if(s.lines.length!==rows[i][1].length)throw Error('Paragraph mismatch '+s.id);return {id:s.id,title:rows[i][0],lines:rows[i][1]};})};
fs.writeFileSync(path.join(__dirname,'../script/narration.en.json'),JSON.stringify(result,null,2)+'\n');console.log('34 scenes / '+result.scenes.reduce((n,s)=>n+s.lines.length,0)+' aligned English paragraphs.');
