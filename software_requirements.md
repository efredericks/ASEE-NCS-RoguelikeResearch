# Software Requirements

This document presents our initial software requirements specification.  Each sub-bullet indicates a possible test to ensure the requirement is being satisfied.

---

1. Map is generated according to the appropriate procedural generation technique
  - proc gen technique being used by engine == one selected/desired for that given level?

2. Sub-areas outside of the map are destroyed after creation so that the player can access
all floor tiles on the map.
  - Does floodfill from the players position cover all floor tiles?

3. Items are placed only within the playable area
  - Does floodfill from the players position reach all the items on the map?

4. Enemies are placed only within the playable area,
  - Does floodfill from the players position reach all enemies on the map?

5. Each floor is able to be beaten
  - Could be very hard to measure, maybe using the auto explore to test beat levels? (still need to create autoexplore)
b. Extra data structure that logs neighboring cells (helper functions)

6. Item damage, gear damage, and enemy scaling is adequate as levels progress.
  - Do things scale as gameplay progresses, maybe by a certain amount?

7. Final boss and sub-bosses spawn at the appropriate levels and have adequate gameplay interactions, wether it is dropping items or ending the game.
  - Tests to ensure bosses spawn and drop the relevant items or end the game

8. Relevant hud and gameplay menus function correctly
  - At desired x, y coordinates

9. Items function correctly
  - Is each item able to be used, dropped, or equipped.

10. Message history functions correctly
  - Does each message appear in the message history? Does len(message\_log) == output?

11. Is the playable area within the desired range?
  - Does flood fill return an area of 1000 tiles or more.

12. Does the game properly load and save files?
  - Is the given save file added to the game files?

13. Are keyboard inputs registered properly for each event\_handler?
