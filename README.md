## Ivyhacks: Copy Chess

## Inspiration
I'm a competitive chess player and part of my training regimen is playing blindfold against computer chess engines of varying difficulty. However, most modern chess engines are inherently terrible at approximating a desired playing strength because of the way they are designed: most modern chess engines try to find the best continuation given a depth (how many layers of a game tree it can look through). So in order to play at a lower level, chess engines will make a series of perfect moves but with a few egregious mistakes mixed, which makes it easy to identify when you're playing a computer rather than a human. This prompted me to think about creating a human-like engine. 

This thought then expanded to the possibility of simulating a particular opponent's playstyle. For instance, if I play 300 competitive games a year and lose a third of them, could I have an engine that identifies the playstyle of the players I lose to? And another interesting thought then developed: could I identify the playstyle of players from the past and simulate a game between them and players of today? As a chess enthusiast, it would be fascinating to watch two bots simulating, for instance, Bobby Fischer and Magnus Carlsen play against each other - two world champions of chess from different eras.

Lastly, what really inspired me to create this project rather than another was what Michael Seibel said during his keynote: (paraphrasing) 
* **when picking a problem, pick one that will hack your motivation - one that you can work on irrationally even with minimal progress**
* **good founders are uniquely capable to solve a problem**

## How it was built
I began by manually fetching the game data for Magnus Carlsen and Robert James Fischer and writing a script to collect data for an arbitrary user on the Lichess. Then, I read papers discussing differnet implementations and model architectures to predict the best move given some chess position. I tried representing the data in a couple different (but seemingly widely used) formats: bitboards of length 768 (8x8 for a chessboard by 12, the number of different pieces for both white and black) and the same bitboard but with additional contextual information. Once I had decided on the data representation, I iterated through the games of the player provided, and, in addition to storing the position they played, I created data for the same board position if they had played a different move. These two datasets indicate the positions the player preferred over the ones they didn't (otherwise it would have been played). 

Once the datasets for a player are created, a binary-classification model using keras is trained on the data to identify if the player would have liked the position after a move. After the model is trained, it can be played against by combining the model with an alpha-beta pruning algorithm, an algorithm to identify the best path in a game tree by assigning value to each position and its subsequent positions. Instead of assigning a value to the position and comparing values, as one normally would, the model is presented with two positions and the one with the higher probability of being played is selected.

On the front-end, I developed a mobile-application using Framework-7 and Vue.js, to which I can apply cordova, a web-wrapper, to create a multi-platform mobile application. The user authentication was done using Firebase and user data was stored in Firestore. The back-end, which connected the front-end to the model, was written in python using Flask.

## Challenges I ran into
Normally, as a data scientist, I only work on the back-end developing the desired model for a project, so I ran into numerous issues in developing the front-end of the app, especially as I had never worked with Vue before and my experiences with Flask is limited. Moreover, in addition to functional issues on the front-end, I also ran into design issues.

## What I learned
I learned how to use Vue in conjunction with Flask, Firebase, and Firestore, and, truthfully, I learned that I prefer working on the back-end development of an app - that being said, by trying and learning new things I got to experience the sheer joy of toiling with a problem and solving it, which, while I can experience on the back-end, the time spent toiling and thus the corresponding joy by solving the problem is lesser.

## What's next for Copy Chess?
[ Copy Chess is currenlty being developed in a Private Repository for the Microsoft Azure Hackathon ]
* I intend to rework the model design including both more contextual information (centipawn-differential between moves, most frequently missed tactics - built using a tactics classifier, etc)
* Fully flesh out the training queue (so you can select only models that have been trained) and perhaps create a restriction on the number of models a user can train
    * Also, implement the option to train on the players a given player loses to rather than the player itself
* Upload the back-end to the cloud, heroku, app engine, etc, so it functions better as a standalone app
* Include a styleometry report, more formalised description of style, for both the given player and their victorious opponents, so one can identify areas to improve on more easily
* Blindfold Option when playing
* Outputs a copy-able PGN beneath the Game once finished, and being able to run a report within the app of the game you just played
* Publish to the app store
