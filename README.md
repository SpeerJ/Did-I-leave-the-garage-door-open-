# Did I leave the garage door open?

People keep leaving the garage door open, it's unsafe, it's irritating to the other tenants, and it's solvable with computer vision!

----


Here in Guayaquil safety is very important, houses are typically walled off, and use broken glass or electric fences to deter would be thieves or home invaders. To fight the recurring issue of having an open garage door I've created a very simple script to submit a message to your whatsapp group if you have an open garage door.

It leverages opencv and especially the flood fill algorithm to determine whether you're looking at a garage door or not.

----
This is an MIT licensed project with some inspiration from https://answers.opencv.org/question/56779/detect-open-door-with-traincascade/. 
