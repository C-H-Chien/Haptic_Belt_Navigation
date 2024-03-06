##LIGHTS
import viz
##This is a simple helper script that all runtime programs will call
#In it the overhead and 4 side lights that have been traditionally employed in VENLab experiments are added to the environment
#And they will remain on throughout the experiment.
#If you are designing an experiment in which the lights need to be manipulated then this script should not be imported at the top of your code
light1 = viz.addLight() #Add an overhead light
light1.setEuler(0,90,0)
light2 = viz.addLight() #Next four are lights from each direction to ensure even lighting
light2.setEuler(90,0,0)
light3 = viz.addLight()
light3.setEuler(0,0,0)
light4 = viz.addLight()
light4.setEuler(180,0,0)
light5 = viz.addLight()
light5.setEuler(270,0,0)