# Mister-CP-SAT

CP-SAT solver for the [Mister](https://github.com/GILD-Studios/mister) app developed with Google's [OR-Tools](https://developers.google.com/optimization) package.

---

Generate **N** equally matched football teams given a list of players, the group size _n_ of an _n_-a-side football pitch, with _n_ being either 5, 6, or 7, the formation and the number of teams **N**.

Each player has a name, a position and a rating. The position can either be _F_, for Forward, _M_, for Midfielder, and _D_, for Defender, while there's no signature letter for Goalkeepers as, granted a relatively small football pitch, they are assumed to be either flying or rotating between the players; the rating, instead, is between 0 and 100.  

The objective is to construct **N** groups whose sum of ratings is as close to the average as possible. Furthermore, depending on the group size _n_ and on the formation, a certain number of positions have to be covered, say k_i, with i being either _F_, _M_, or _D_, such that at least k players of the i-th position are in each group.
