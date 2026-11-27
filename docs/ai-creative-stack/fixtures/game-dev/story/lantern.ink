// An original three-ending story used by the ink-branches check.
VAR courage = 0
VAR coins = 0
VAR ending = ""

The tide is out and the lighthouse lamp has gone dark.
-> shore

=== shore ===
A gull drops a brass key at your feet.
* [Climb the lighthouse stairs]
    ~ courage = courage + 1
    You take the stairs two at a time.
    -> stairs
* [Search the rock pools]
    ~ coins = coins + 3
    Three old coins glint between the weeds.
    -> pools

=== stairs ===
Halfway up, the wind howls through a broken window.
* [Keep climbing]
    ~ courage = courage + 1
    -> lamp
* [Go back down]
    -> pools

=== pools ===
A crab guards a tin box half buried in sand.
* {coins >= 3} [Trade a coin for the box]
    ~ coins = coins - 1
    -> box
* [Wait for the tide]
    -> tide

=== lamp ===
The brass key fits the lamp housing. You light it.
~ ending = "beacon"
The ships turn safely past the reef. THE END (courage {courage}).
-> END

=== box ===
Inside the box is a map to a cove nobody has charted.
~ ending = "map"
You keep the map and {coins} coins. THE END.
-> END

=== tide ===
The water rises around your boots and you head home.
~ ending = "home"
THE END.
-> END
