const fs=require('fs'),path=require('path');
const translations={
'01':[
'We hear a lot these days about how hard it is to get a developer job. When I talk to computer science students, one question comes up often: "Has AI made it harder to get hired as a developer?"',
'AI really does write code very well now. A few prompts can produce a simple program or game. When an error occurs, you can paste the error message into AI and ask it to fix it.'
],
'02':[
'That can naturally lead to this thought: "Do I even need to be good at coding myself anymore?" But after working as a developer and teaching students programming, I find myself asking the opposite question.',
'In the age of AI, why should a company hire a junior developer? More specifically, why should it hire a junior who can only make a program with AI?',
'That is what I want to discuss today.'
],
'03':[
'First, I am not saying AI has had no effect on developer hiring. It clearly has. But consider the statement: "It is hard to find a job because AI is replacing developers."',
'I do not think that one sentence is enough to explain the entire junior hiring problem. If you search for C++ developers on Korean job sites such as Saramin or JobKorea, you can still find a substantial number of job listings.'
],
'04':[
'Of course, we should not take that number at face value. It includes experienced positions. A listing that contains the keyword C++ does not necessarily mean a pure C++ role for a new graduate.',
'So I am not saying, "There are lots of listings, so the hiring crisis is a lie." My question is different. Companies are still looking for developers. Why is it so hard for junior developers to get hired?'
],
'05':[
'Here I want to ask a somewhat uncomfortable question. Imagine a computer science student whose GPA is close to 4.0. They have studied C++.',
'They have studied data structures and algorithms. They can even explain what a linked list is. But suppose we turn off the internet and AI, give them an empty project, and say, "Implement a linked list from scratch."'
],
'06':[
'What would happen? Or, to make it a little more complex, what if we said, "Build a simple Tetris game from scratch"? Within my own experience teaching students, more people get stuck here than you might expect.',
'Of course, this is my personal teaching experience. I am not saying every computer science student is like this. But I think it reveals an extremely important distinction.',
'Reading code and writing code are different abilities.'
],
'07':[
'I think programming is similar to learning English. Imagine someone who has studied English grammar very hard. Show them a sentence and they can interpret it.',
'They can find the subject and verb and explain the grammar. But then bring in an English speaker and say, "Have a conversation in English for the next 30 minutes."',
'That becomes a completely different problem. Knowing English grammar and conversing in English are different things. Programming is similar. Show them linked list code, and they can explain it.'
],
'08':[
'They understand that there is a Node and a Next Pointer, and that the pointer points to the next node. But give them a blank screen and say, "Build it yourself."',
'Now the situation changes. How do I define a Node? Where do I manage Head? How do I insert a node? How should the links change when I delete one?',
'What if I delete the last node? When do I free the memory? They have to produce all of this from their own mind. I think this is programming proficiency, which is different from simply knowing programming syntax.'
],
'09':[
'Tell someone making Tetris for the first time, "Build Tetris," and they may not know where to begin. But someone who has built small programs or games themselves many times is different.',
'When asked to build Tetris, they naturally start breaking the problem down. I will need input. I will need blocks. I will need a board. I will need collision detection.',
'I will need rotation. I will need to check whether a row is complete. In what order should the game loop update everything? These questions begin to arise naturally.'
],
'10':[
'It is not because they memorized the code. They have repeatedly experienced turning a problem into a program structure. It is like someone who has practiced English conversation extensively: they do not solve a grammar exercise in their head before every sentence.',
'Ultimately, programming also requires repeated practice.'
],
'11':[
'This is where AI enters the picture. Now a student building Tetris does not have to think through everything from beginning to end. They can ask AI, "Make Tetris in C++."',
'Code appears. If it has a compilation error, they say, "Fix this error." If they need a new feature, they say, "Add a display for the next block."',
'This means someone can create a fairly convincing result without much programming proficiency. But we should be careful not to misunderstand the point.'
],
'12':[
'I am not saying that using AI is itself a problem. I use AI. Experienced developers use AI too. The ability to use AI effectively will become extremely important for developers.',
'So we need to change the question.'
],
'13':[
'Of course such a developer can have value. Being unable to make Tetris without AI does not automatically make someone worthless as a developer. If they can use AI to deliver what a company needs quickly, that is an ability too.',
'But what matters is how they use AI. Imagine two developers. The first receives a requirement and passes it straight to AI.'
],
'14':[
'They receive code. An error occurs. They paste the error message into AI. AI fixes it. They run it. It works. They are done. The second person also uses AI.',
'But first they break down the problem. They identify which systems need to change. They decide on a structure. They delegate the implementation they need to AI. They integrate the generated code with the existing code.',
'When a problem occurs, they use a debugger and profiler to find the cause. They change the design if necessary. Then they use AI again. Both people used AI.'
],
'15':[
'Both might even develop much more slowly without AI than they do now. But from the company\'s perspective, the two do not have the same value.'
],
'16':[
'That is why I also disagree with the claim that "real developers must code without AI." That is not the important point. When AI is available, there is no need to write every repetitive line by hand.',
'At work, we search, read official documentation and existing code, ask colleagues, and use AI. What matters is not how many lines we can write without AI. It is whether we can solve problems independently using tools, including AI.'
],
'17':[
'Someone whose productivity is increased by AI is different from someone who cannot even figure out how to turn a problem into a program without AI.'
],
'18':[
'Suppose a junior developer\'s job is to receive requirements, pass them to AI, generate code, ask AI again when an error occurs, and submit the result. A company might think the following.',
'"Then why should we hire this person?" The company already has experienced developers. It has people who know the existing project, understand its systems, can break down problems, design solutions, and debug.'
],
'19':[
'Crucially, those experienced developers can use the same AI. They can analyze the problem, design the structure, use AI to speed up implementation, verify the generated code, and debug when problems occur.',
'Finally, they can apply the result to the actual service. In this environment, the economic reason to hire several junior developers for simple implementation work may become weaker than it used to be.'
],
'20':[
'Let us talk about the game industry. You might think game development means making a game, releasing it, and finishing. But live service projects, including online and mobile games, are an important part of major Korean game companies.',
'For these games, release is not the end. It is closer to the beginning. Development continues after launch. New characters and items are added.'
],
'21':[
'Content and events are added. Balance is adjusted. Servers and clients keep changing. Bugs appear after updates. When a live incident occurs, someone has to find its cause quickly.',
'And this process repeats for years.'
],
'22':[
'Suppose you use AI to build an inventory system. For a personal project, you might be finished once it works. A live project is different.',
'One day a designer says, "Please add an item-locking feature." At first it sounds very simple. But in a real project, there is a lot to consider.',
'What about selling? Dropping? Trading? Moving items to storage? Upgrading? Equipping? Server persistence? The client UI? Network synchronization? Then, six months later, the requirement changes.'
],
'23':[
'"Allow locked items to be upgraded during certain events." Now you have to add another feature on top of the code you wrote before. In a live service, generating new code is not the only important ability. You also need to understand the existing system and safely build changes on top of it.'
],
'24':[
'Building a small project from scratch with AI is different from joining a huge codebase written by many developers over several years and being asked, "Find the cause of this bug."',
'You have to find where the problem occurs. You need to understand why the existing code was written this way.',
'You also need to consider how changing it will affect other systems. You have to implement new requirements without breaking existing features.'
],
'25':[
'When an incident occurs in a running service, you must trace its cause. You cannot simply say, "Let us ask AI to rebuild it from scratch."',
'It is already running and connected to countless other systems. That is why live service development requires not just a Feature Creator, but also a Problem Solver and a System Maintainer.'
],
'26':[
'Consider junior developer A. With AI, they can make games and implement features. But without AI, they get stuck even on how to break a problem down.',
'Junior developer B also uses AI actively. But they can read existing code, break down the problem, identify what to change, delegate the necessary work to AI, verify the result, and debug problems themselves.'
],
'27':[
'The company is not deciding between someone who uses AI and someone who does not. The more important difference going forward may be between someone who depends on AI and someone who uses it as a tool.'
],
'28':[
'In the past, companies could give junior developers relatively small tasks. Build this UI. Parse this data. Implement this class.',
'Write this repetitive code. Through these tasks, juniors gained experience with a real codebase. Senior colleagues reviewed their code. They made mistakes.'
],
'29':[
'They also debugged, gradually growing into developers who could take responsibility for larger systems. Then AI arrived. Experienced developers can now use AI to complete some of the simple implementation work once assigned to juniors much faster.',
'From the company\'s perspective, some of those small tasks that could be given to juniors may therefore shrink. I think this is an extremely important problem for junior developers in the age of AI.'
],
'30':[
'Before AI eliminates developers, it is reducing some of the first steps that juniors used to take on the way to becoming experienced developers. Paradoxically, the starting level expected of a junior may rise as a result.'
],
'31':[
'Here is something I particularly want to tell first- and second-year computer science students. During those years, try to build programs yourself without AI whenever possible.',
'But the meaning of "build it yourself" matters here. Simply copying code from a book instead of looking at AI-generated code is not the practice I mean.'
],
'32':[
'Finding someone else\'s code online and copying it. Watching a YouTube tutorial and typing exactly what the instructor types. Keeping a finished example from a book open beside you and copying it.',
'These are also different from producing a program from a blank project. Of course, I am not saying this kind of study is bad. When learning a concept for the first time, you need to read books.'
],
'33':[
'You need to watch lessons and read plenty of good code. Asking AI about a concept can also help. But you must distinguish practice in reading and understanding code from practice in producing code when you start with nothing.'
],
'34':[
'Suppose you are studying linked lists. First you read a book. You learn what a Node is. You learn how a pointer points to the next node.',
'You study the principles of insertion and deletion. Of course you need references up to this point. But once you have finished studying, close the book. Turn off the internet. Turn off AI.',
'Close the example code too. Then create an empty project. Start with nothing on the screen. "All right, let us build a linked list."'
],
'35':[
'At first, you might get stuck on "How did I declare a Node?" But that very moment matters. The part where you get stuck is the part that has not yet become your own.'
],
'36':[
'Suppose you followed a YouTube tutorial on making Tetris from beginning to end. In the video, the instructor creates the Board and Block, then implements Collision, Rotation, and Line Clear.',
'The student follows along exactly. At the end, Tetris runs. But there is one more thing to try. Close the project. Turn off the lesson.'
],
'37':[
'Do not look at the source code either. Create a new, empty project. Now try making Tetris again. Suddenly, it becomes a completely different problem.',
'"What should I build first?" "Where should I store the block data?" "Should the board use a two-dimensional array?" "When should I check collisions?" "How should I rotate a block?"',
'"In what order should the game loop run?" I have to answer these questions, not the instructor. This is the process I mean by coding practice.'
],
'38':[
'This is something I especially want to emphasize to first- and second-year computer science students. During those years, turn off AI and, if possible, avoid looking at solution code. Build a program yourself from a blank project.',
'The meaning of "build it yourself" matters here. I am not only talking about following along with AI-generated code.'
],
'39':[
'Finding someone else\'s code online and copying it. Watching a YouTube lesson and typing exactly what the instructor writes. Keeping a completed example from a book open beside you and copying it.',
'These are also different from the blank-project practice I am discussing. Of course, these study methods are not inherently bad. When first learning a concept, you need examples from books, lessons, and plenty of good code written by other developers.'
],
'40':[
'But we need to distinguish practice in reading and understanding code from practice in creating code when we start with nothing.'
],
'41':[
'Suppose you are studying linked lists. First you read a book. You learn what a Node is, how a pointer points to the next node, and how insertion and deletion work.',
'Of course, you need references up to this point. But once you have finished studying, close the book. Turn off the internet and AI, and close the example code. Then create an empty project.'
],
'42':[
'This is all that is on the screen. Now begin. Build a linked list yourself. At first, you might get stuck on "How did I create a Node?"',
'That is okay. The very moment you get stuck reveals a part you have not yet made your own.'
],
'43':[
'Suppose you followed a YouTube tutorial on making Tetris from beginning to end. In the video, the instructor creates the Board and Block, then implements Collision, Rotation, and Line Clear.',
'The student follows along exactly. At the end, Tetris runs. But there is one more thing to try. Close the project. Turn off the lesson.'
],
'44':[
'Do not look at the source code either. Create a new, empty project. Now try making Tetris again. Suddenly, it becomes a completely different problem.',
'"What should I build first?" "Where should I store the block data?" "Should the board use a two-dimensional array?" "When should I check collisions?" "How should I rotate a block?"',
'"In what order should the game loop run?" I have to answer these questions, not the instructor. This is the process I mean by coding practice.'
],
'45':[
'I consider this distinction extremely important. Reading code produced by AI and thinking, "Oh, that is how to do it." Reading a book\'s example and thinking, "Oh, that is how a linked list is implemented."',
'Looking at someone\'s GitHub code and thinking, "So that is the structure they used." This kind of study is necessary too.',
'But repeating only that mainly trains Recognition: recognizing what you see. Making a program from a blank project is different.'
],
'46':[
'The answer is not in front of you. You have to remember, break down the problem, choose the data structures, create functions and classes, and decide the implementation order.',
'And when something is wrong, you have to find the cause. This is closer to practicing Recall and Problem Solving together.'
],
'47':[
'Suppose you have read 1,000 English sentences. You can understand all of them when you see them. But close the book and sit down in front of an English speaker, and suddenly you may find that nothing comes out.',
'Understanding English that you see and producing sentences to express your own thoughts require different practice. Programming is similar. Reading linked list code ten times and building a linked list from scratch ten times are not the same practice.'
],
'48':[
'Understanding Tetris code and creating its structure yourself in an empty project are not the same practice either. So the study method I recommend is simple.',
'Look at materials when you learn. Read books, watch lessons, and listen to AI\'s explanations. But once you understand reasonably well, close everything. Then build it again from a blank project.'
],
'49':[
'There is one important point here. You will naturally get stuck when starting from a blank project. That is normal. You might not even remember how to declare a Node.',
'Pointers may confuse you. You might think for a long time about collision detection. You might spend two hours unable to find a single bug.'
],
'50':[
'But I think that time is extremely important. A problem you could solve in ten seconds with the solution beside you becomes something you think about for thirty minutes. You change code, set a breakpoint, inspect variables, fail, and build it again.',
'That process trains your ability to turn problems into code. If the goal is to finish an assignment quickly, using AI is much more efficient. But if the goal is to learn programming, the fastest path may not always be the best way to learn.'
],
'51':[
'For first- and second-year university students, I recommend deliberately making plenty of time for this. After studying a data structure, close the solution and implement it yourself.',
'After studying an algorithm, close the explanation and solve it again. After studying game programming, finish the lesson and rebuild it in an empty project.',
'If possible, avoid immediately asking AI for the solution code. Give yourself enough time to think and produce code from scratch. On the other hand, once you have built basic programming proficiency, I think it is fine to use AI actively.'
],
'52':[
'As your projects grow in your third and fourth years, use AI to improve productivity. Use it to generate repetitive code, investigate libraries, write tests, get refactoring ideas, and quickly learn unfamiliar technologies.',
'Once you enter the workplace, AI can be a powerful productivity tool. My message is not "Do not use AI."',
'It is "Do not outsource the thinking process while you are learning programming."'
],
'53':[
'The goal is not to become someone who develops without AI. Nor is it to become a developer who never reads books or searches for information.',
'At work, of course we read documentation and existing code, consult Stack Overflow, use AI, and ask colleagues. But while using those tools, the ability to turn a problem into a program must also exist in our own minds.'
],
'54':[
'That is why I hope computer science students spend at least their first two years gaining lots of experience building programs from blank projects. After learning, close the book.',
'Turn off the lesson. Turn off AI too. Open an empty project. Start for yourself with nothing there. At first you will be very bad at it. But with repetition, at some point the structure of the code will begin to form in your mind as soon as you see a problem.'
],
'55':[
'Then try using AI again. From that point on, AI becomes a tool that implements your ideas much faster, rather than one that thinks in your place.'
],
'56':[
'If you study alone and do not know where to begin, collect the code you have built and the points where you got stuck. Through Yamyam Coding programming coaching and tutoring, we can review your study direction together.',
'I will leave the tutoring link in the video description, on the final screen, and in the pinned comment. Let us build your ability to think, design, and implement for yourself, starting with that first small step.'
]};
const ko=JSON.parse(fs.readFileSync(path.join(__dirname,'narration.ko.json'),'utf8'));
const en={...ko,language:'en',title:'Why Junior Developers Struggle to Get Hired in the AI Era',scenes:ko.scenes.map(s=>{const lines=translations[s.id];if(!lines||lines.length!==s.lines.length)throw Error('Paragraph alignment '+s.id);return {...s,lines};})};
fs.writeFileSync(path.join(__dirname,'narration.en.json'),JSON.stringify(en,null,2)+'\n');
console.log('Faithful English translation: '+en.scenes.length+' scenes, '+en.scenes.reduce((n,s)=>n+s.lines.length,0)+' aligned paragraphs.');
