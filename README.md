# Urlaubsvorschlager

## Konzept

Ähnlichkeit der Personen nach Ähnlichkeit ihrer Reiseziele definieren. Und zwar so: 
Ein Reiseziel, das von Person A und Person B gleich weit entfernt ist, und das beide besucht haben trägt stark zum Ähnlichkeitsscore bei. Eines, das bei A in der Nähe ist und das dieser besucht hat, das aber von B weit entfernt ist und dieser nicht besucht hat ist irrelevant. Beispiel: A lebt in Madrid. Er war in Barcelona auf Urlaub. B lebt in Weißrussland und war nicht in Barcelona. Dass A in Barcelona war und B nicht sagt nichts über deren Reisezielähnlichkeit aus, da es ja für B ungleich schwieriger sein würde nach Barcelona zu gelangen als für A. 
So, jetzt hat man einen Ähnlichkeitswert für jede Person zu jeder Person O(n^2). 

Als nächstes sortiert man alle möglichen Reiseziele (alle, die es gibt) nach dem Ähnlichkeitswert der Leute, die dort waren. Man kriegt also eine sortierte Liste, das erste Element ist das Reiseziel, an dem die meisten Leute mit einem hohen Ähnlichkeitswert waren. 

Dann eine Heatmap machen: Wenn jemand in Mailand war und auch in Como, dann ist die Lombardei als ganzes ziemlich relevant. 

## Ähnlichkeit
Sagen wir Nutzer A ist der Nutzer, für den Urlaubsvorschläge berechnet werden sollen. Nutzer B ist ein beliebiger Nutzer in der Datenbank, zu dem gerade der Ähnlichkeitswert berechnet wird. 

Fall 1: Nutzer A hat 10 besuchte Orte, Nutzer B 100. Wir nehmen für jeden der 10 von A besuchten Orten den Ort von B, der ihm am ähnlichsten ist für den Ähnlichkeitswert.

Fall 2: Nutzer A hat 100 besuchte Orte, Nutzer B 10. Wir nehmen noch immer für jeden von As Orten denjenigen von B, der am ähnlichsten ist. Orte von B können dabei "recycelt" werden: Z.B. Nutzer A war in Paris im Louvre und auch am Eiffelturm. Nutzer B checkt im Allgemeinen weniger oft ein als Nutzer A, er hat nur am Eiffelturm eingecheckt. 
Nun teilen wir dem Checkin "Louvre" von Nutzer A "Eiffelturm" von Nutzer B zu, da dies der ähnlichste Checkin ist. Dem Checkin "Eiffelturm" von Nutzer A teilen wir ebenfalls "Eiffelturm" von Nutzer B zu, da er am ähnlichsten ist. "Eiffelturm" von Nutzer B wurde also mehrfach verwendet. 