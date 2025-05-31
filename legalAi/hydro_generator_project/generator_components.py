import adsk.core, adsk.fusion, adsk.cam, traceback

def create_turbine():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5.0)
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(10.0)
        extInput.setDistanceExtent(False, distance)
        extrudes.add(extInput)
    except:
        print('Failed creating turbine:', traceback.format_exc())

def create_rotor():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 3.0)
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(8.0)
        extInput.setDistanceExtent(False, distance)
        extrudes.add(extInput)
    except:
        print('Failed creating rotor:', traceback.format_exc())

def create_stator():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 4.0)
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(6.0)
        extInput.setDistanceExtent(False, distance)
        extrudes.add(extInput)
    except:
        print('Failed creating stator:', traceback.format_exc())

def create_housing():
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 6.0)
        extrudes = rootComp.features.extrudeFeatures
        prof = sketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(12.0)
        extInput.setDistanceExtent(False, distance)
        extrudes.add(extInput)
    except:
        print('Failed creating housing:', traceback.format_exc())

# Main function to create all components
def main():
    create_turbine()
    create_rotor()
    create_stator()
    create_housing()

if __name__ == '__main__':
    main()
