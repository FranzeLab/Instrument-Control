# Python code for ExperimentPlanner
from com.jpk.spm.afm.inst.lib import SPMScript
##################################################################################
##################################################################################
# This routine executes force measurements in a defined grid, starting at the lower left corner.
# An optical image of the sample is captured at the end of each column of measurements in the grid.
##################################################################################
##################################################################################

#The following 6 user defined parameters must be entered:

# 1. Position right upper corner in motorised stage meter
xPosition2 = 2812e-6
yPosition2 = -394e-6
 
# 2. Position left lower corner in motorised stage meter
xPosition = 2494e-6
yPosition = -537e-6
   
# 3. Define Number (measurement index from which to start the script; 0 = start at beginnning)
Number = 0

# 4. Approach Height (from JPK software)
App = 5.0e-05

# 5. Define Resolution
resolution = 20e-6

# 6. Folder
Date = time.strftime("%Y.%m.%d", time.localtime())
Directory = '/home/jpkroot/jpkdata/YYY.MM.DD/sample1'
import os
#os.makedirs(Directory+'/Pics/')


##################################################################################
##################################################################################

xLength = abs(xPosition - xPosition2)
yLength = abs(yPosition - yPosition2)

# Sets up grid
# Grid size (in meters):
fastLength = (int (xLength / resolution) * resolution) + resolution
slowLength = (int (yLength / resolution) * resolution) + resolution

# Grid position.  These coordinates describe the center of the grid
# (in meters).

xGridCenterPos = xPosition + ((int (xLength / resolution) * resolution) / 2)
yGridCenterPos = yPosition + ((int (yLength / resolution) * resolution) / 2)

# Number of positions in the grid:
numFastPoints = int (xLength / resolution) + 1
numSlowPoints = int (yLength / resolution) + 1
totalPoints = numFastPoints * numSlowPoints

# Grid angle.  This value is the angle between fast direction and x
# direction (in degrees):
gridAngle = 0

# Set the temperature controller to 38.5°C.  This assumes the
# temperature controller window has already been opened:
# TemperatureController.setTemperature(38.5)
# Wait until the requested temperature is reached:
# TemperatureController.waitForTemperature()

# Activate autosave:
Spectroscopy.setAutosave(True)
# Set the target directory for storing the collected curves:
Spectroscopy.setOutputDirectory(Directory)

# Create the grid:
ForceSpectroscopy.setGridPattern(
    fastLength, slowLength,
    xGridCenterPos, yGridCenterPos,
    numFastPoints, numSlowPoints,
    gridAngle
    )

# Iterate through the grid.  This is currently implemented using two
# nested loops to allow pauses between the rows:
Xmax=ForceSpectroscopy.getForcePosition((totalPoints) - 1).getX()
for index in range(Number,totalPoints):
        Spectroscopy.moveToForcePositionIndex(index)
        X=ForceSpectroscopy.getForcePosition(index).getX()
        Y=ForceSpectroscopy.getForcePosition(index).getY()
        print index
        if index==Number:
            VertDef1=Channels.getValue('Vertical deflection', 'volts')
            print VertDef1
            #print index
            Scanner.approach()
            gg = Scanner.getCurrentHeight()
            Scanner.retractPiezo()
            SPMScript.moveScanner(-150*1e-6)
                              
        SPMScript.moveScanner(148*1e-6)
        time.sleep(.05)
        VertDef2=Channels.getValue('Vertical deflection', 'volts')
        print VertDef2
        
        SUMMME=Channels.getValue('photo-sum', 'volts')
        
        if SUMMME<0.5:
            #VertDef1=Channels.getValue('Vertical deflection', 'volts')
            #print VertDef1
            #print index
            SPMScript.moveScanner(-250*1e-6)
            Scanner.approach()
            gg = Scanner.getCurrentHeight()
            Scanner.retractPiezo()
            #SPMScript.moveScanner(-250*1e-6)
            
       
        if abs(VertDef1-VertDef2)>2.5:
            print 'New Aproach'
            SPMScript.moveScanner(-100*1e-6)
            Scanner.approach()
            gg = Scanner.getCurrentHeight()
            Scanner.retractPiezo()
            time.sleep(.05)
            VertDef1=Channels.getValue('Vertical deflection', 'volts')
            print VertDef1
        else:
            VertDef1=VertDef2
            print 'New Aproach'
            SPMScript.moveScanner(-100*1e-6)
            Scanner.approach()
            gg = Scanner.getCurrentHeight()
            Scanner.retractPiezo()
            time.sleep(.05)
            VertDef1=Channels.getValue('Vertical deflection', 'volts')
            print VertDef1
           
        # Start the spectroscopy scan(s).  The parameter specifies the
        # number of scans to take at the current position:
        Time = time.strftime("%H.%M.%S", time.localtime())
        Date2 = time.strftime("%Y.%m.%d", time.localtime())
        #Snapshooter.saveOpticalSnapshot(Directory+'/Pics/'+Date2+'-'+Time)
        #ForceSpectroscopy.startScanning(seriesCount = 1, endOption = ForceScanningEndOption.APPROACH_PIEZO)
        #kk = Scanner.getCurrentHeight()
        ForceSpectroscopy.startScanning(seriesCount = 1, endOption = ForceScanningEndOption.RETRACT_PIEZO)
        time.sleep(.1)
        series = ForceSpectroscopy.getCurrentSeries()
        segments = series.segments 
        segment = segments['Retract'] 
        data = segment.getData('capacitiveSensorHeight','nominal')
        data2 = segment.getData('Height','nominal')
        minHeightM = data.minimumValue
        minHeight = data2.minimumValue
        #print 'Minimum HeightMeasured was  ' + str(minHeightM*1e6) + 'um'
        print 'Minimum PiezoHeight was         ' + str(minHeight*1e6) +'um'
        #Scanner.retractPiezo()
        if minHeight<1e-06:
            Scanner.approach()
            minHeight = Scanner.getCurrentHeight()
            Scanner.retractPiezo()
            ForceSpectroscopy.startScanning(seriesCount = 1, endOption = ForceScanningEndOption.RETRACT_PIEZO)
            
        if abs(gg-minHeight)>0.5e-05:
            SPMScript.moveScanner(gg-minHeight)
            gg = App
            

        if index%100==99:
            Scanner.approach()
            gg = Scanner.getCurrentHeight()
            Scanner.retractPiezo()

        SPMScript.moveScanner(-100*1e-6)

        if X==Xmax:
            MotorizedStage.engage()
            MotorizedStage.moveToAbsolutePosition(xGridCenterPos, yPosition2, 200*1e-6)
            time.sleep(2)
            Snapshooter.saveOpticalSnapshot(Directory+'/Pics/'+Date2+'-'+Time)
            MotorizedStage.moveToAbsolutePosition(X, Y, 200*1e-6)
            MotorizedStage.disengage()

        
        
# Dectivate autosave:
Spectroscopy.setAutosave(False)

##################################################################################
##################################################################################    
