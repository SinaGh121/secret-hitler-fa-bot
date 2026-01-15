# Secret Hitler Rules (Detailed Reference)

This is a detailed, implementation-ready reference based on the official rulebook in
`Rules/Secret_Hitler_Rules.pdf`. It is intended for precise game behavior.

## Components and counts
- Policy tiles: 17 total (6 Liberal, 11 Fascist).
- Secret Role cards: 10 total (Liberals, Fascists, Hitler).
- Party Membership cards: 10 total (6 Liberal, 4 Fascist).
- Ballot cards: 10 "Ja!" and 10 "Nein".
- Boards: use the board matching player count (5-6, 7-8, 9-10).
- President placard and Chancellor placard.
- Election Tracker marker, Draw pile card, Discard pile card.

## Roles and teams
- Teams: Liberal team and Fascist team.
- Roles: Liberal, Fascist, and Hitler (Hitler is on the Fascist team).
- Party Membership cards hide whether a Fascist is Hitler or an ordinary Fascist.

## Role distribution by player count
| Players | Liberals | Fascists | Hitler |
|---------|----------|----------|--------|
| 5       | 3        | 1        | 1      |
| 6       | 4        | 1        | 1      |
| 7       | 4        | 2        | 1      |
| 8       | 5        | 2        | 1      |
| 9       | 5        | 3        | 1      |
| 10      | 6        | 3        | 1      |

## Setup
- Choose the board matching the number of players.
- Shuffle all 17 policy tiles into a face-down policy deck and place on Draw pile.
- Build one envelope per player containing:
  - One Secret Role card.
  - One Party Membership card that matches the role's team.
  - One Ja ballot and one Nein ballot.
- Shuffle envelopes and deal one to each player.
- Knowledge step:
  - 5-6 players: Fascists and Hitler open eyes and see each other.
  - 7-10 players: Fascists (not Hitler) open eyes and see each other; Hitler keeps eyes
    closed and gives a thumbs-up so Fascists identify Hitler. Hitler does not learn the
    Fascists.
- Randomly select the first Presidential Candidate and give them the President placard
  (and initial control of the Chancellor placard).

## Win conditions
- Liberal team wins if:
  - Five Liberal policies are enacted, or
  - Hitler is executed.
- Fascist team wins if:
  - Six Fascist policies are enacted, or
  - Hitler is elected Chancellor after three or more Fascist policies are enacted.

## Round structure
Each round has:
1) Election
2) Legislative Session
3) Executive Action (only if a Fascist policy grants a power)

## Election phase
1) Pass Presidential Candidacy
   - President placard moves clockwise to the next player.
2) Nominate a Chancellor
   - The Presidential Candidate nominates any eligible player for Chancellor.
3) Vote
   - All players vote simultaneously with Ja/Nein.
   - Majority Ja forms a government; tie counts as a failure.
   - If the government is elected and 3+ Fascist policies are enacted:
     - Ask if the new Chancellor is Hitler. If yes, Fascists win immediately.
     - If no, the table now knows the Chancellor is not Hitler.

### Eligibility and term limits
- Term limits apply to the last elected President and last elected Chancellor.
- Term limits affect only the Chancellorship; anyone can be President.
- Term limits apply to last elected officials, not last nominated officials.
- With only 5 players left, only the last elected Chancellor is ineligible; the last
  President may be nominated as Chancellor.
- The Election Tracker and Veto Power can affect eligibility as described below.

## Legislative Session
1) President draws the top three policy tiles.
2) President secretly discards one tile face down.
3) President passes the remaining two tiles to the Chancellor at the same time.
4) Chancellor secretly discards one tile face down and enacts the remaining tile.
5) Place enacted policy face up on the appropriate track.

### Communication and secrecy rules
- The President and Chancellor may not communicate about policy contents during the
  Legislative Session (no verbal or nonverbal signaling).
- The President and Chancellor may not randomize the choice (no shuffling, no "random"
  discards) to avoid responsibility.
- Discarded tiles are never revealed.
- Players may lie about hidden information (policy tiles, investigations).
- The only time a player must tell the truth is when game-ending Hitler conditions are
  triggered: Hitler must reveal if executed or elected Chancellor after 3+ Fascist policies.

### Policy deck maintenance
- If fewer than three tiles remain at the end of a Legislative Session, shuffle the
  Discard pile with the remaining draw pile to form a new policy deck.
- Unused tiles are never revealed and are not simply placed on top without shuffling.

## Election Tracker and chaos
- Each failed election advances the Election Tracker by one.
- After three consecutive failed elections:
  - Reveal and enact the top policy tile immediately.
  - Ignore any power granted by that policy.
  - Reset the Election Tracker to zero.
  - Existing term limits are forgotten; all players are eligible for Chancellor.
  - If fewer than three tiles remain, shuffle Discard with remaining draw pile first.
- Any time a policy is enacted face-up (normal or chaos), reset the Election Tracker.

## Executive Action (Presidential powers)
If a Fascist policy grants a power, the sitting President must use it before the next
round begins. Powers are single-use and do not stack.

### Fascist track powers by player count
| Player count | 1st | 2nd | 3rd | 4th | 5th | 6th |
|--------------|-----|-----|-----|-----|-----|-----|
| 5-6          | None | None | Policy Peek | Execution | Execution | Win |
| 7-8          | None | Investigate | Special Election | Execution | Execution | Win |
| 9-10         | Investigate | Investigate | Special Election | Execution | Execution | Win |

### Investigate Loyalty
- President chooses a player to investigate.
- Investigated player hands over Party Membership card only (not Secret Role).
- President looks in secret, returns the card, may share or lie about the result.
- No player may be investigated twice in the same game.

### Call Special Election
- President chooses any other player to become the next Presidential Candidate.
- Any player can become President, even if term-limited.
- The chosen player runs a normal election immediately.
- After the Special Election, the President placard returns to the left of the President
  who called the Special Election (no players are skipped).

### Policy Peek
- President secretly looks at the top three policy tiles.
- Tiles are returned to the top of the deck without changing the order.

### Execution
- President executes one player.
- If the executed player is Hitler, Liberals win immediately.
- If not Hitler, the executed player's party is not revealed.
- Executed players are removed from the game and may not speak, vote, or run for office.

## Veto power (after 5 Fascist policies)
- After the fifth Fascist policy is enacted, the Executive gains a permanent veto option.
- President draws three tiles and discards one as usual.
- Chancellor may propose a veto instead of enacting a policy.
- If President accepts, both remaining tiles are discarded and the Election Tracker
  advances by one (this counts as an inactive government).
- If President rejects, Chancellor must enact one of the two tiles.

## Open information vs hidden information
- Open information: enacted policy tracks, Election Tracker, current/previous President
  and Chancellor, and execution results (only whether Hitler was executed).
- Hidden information: player roles, party membership, policy tiles in hand or discard,
  and investigation results unless voluntarily disclosed.

## Summary of strict constraints
- No revealing or showing discarded policy tiles.
- No secret signaling or randomization during Legislative Session.
- Hitler must truthfully reveal when executed or when elected Chancellor after 3+ Fascist
  policies (game ends immediately in either case).
