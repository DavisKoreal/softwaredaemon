import adsk.core, adsk.fusion, adsk.cam

def create_turbine():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Create turbine blades
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    # Draw turbine profile (simplified circle for example)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5.0)
    
    # Extrude to create 3D turbine
    extrudes = rootComp.features.extrudeFeatures
    prof = sketch.profiles.item(0)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(1.0)
    extInput.setDistanceExtent(False, distance)
    extrudes.add(extInput)
    
    return 'Turbine created successfully'

def create_generator():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Create generator stator
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    # Draw stator profile (simplified circle for example)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 8.0)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 6.0)
    
    # Extrude to create 3D stator
    extrudes = rootComp.features.extrudeFeatures
    prof = sketch.profiles.item(1)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(3.0)
    extInput.setDistanceExtent(False, distance)
    extrudes.add(extInput)
    
    # Create rotor (simplified cylinder for example)
    sketch = sketches.add(xyPlane)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5.0)
    
    # Extrude rotor
    prof = sketch.profiles.item(0)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(3.0)
    extInput.setDistanceExtent(False, distance)
    extrudes.add(extInput)
    
    return 'Generator component created successfully'

def create_housing():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Create outer housing
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    # Draw housing profile (rectangular for example)
    lines = sketch.sketchCurves.sketchLines
    lines.addTwoPointRectangle(adsk.core.Point3D.create(-10, -10, 0), 
                              adsk.core.Point3D.create(10, 10, 0))
    
    # Extrude to create 3D housing
    extrudes = rootComp.features.extrudeFeatures
    prof = sketch.profiles.item(0)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(10.0)
    extInput.setDistanceExtent(False, distance)
    housing = extrudes.add(extInput)
    
    # Create openings for turbine and generator
    sketch = sketches.add(xyPlane)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 8.5)
    
    # Cut opening
    prof = sketch.profiles.item(0)
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(10.0)
    extInput.setDistanceExtent(False, distance)
    extrudes.add(extInput)
    
    return 'Housing component created successfully'

def assemble_generator():
    # Create all components
    turbine_result = create_turbine()
    generator_result = create_generator()
    housing_result = create_housing()
    
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Get all bodies for positioning
    bodies = rootComp.bRepBodies
    turbine_body = bodies.item(0)
    generator_body = bodies.item(1)
    housing_body = bodies.item(2)
    
    # Position components (simplified example)
    # Move turbine into housing
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, 5)
    turbine_body.transform(transform)
    
    # Move generator into housing
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, 8)
    generator_body.transform(transform)
    
    return 'Generator assembly completed successfully'

# Main execution
if __name__ == '__main__':
    assemble_generator()
