# Cat Map UI Elements Documentation

This document outlines the UI elements and input options used in the cat sighting form to maintain consistency across iOS and web platforms.

## Location Section

### Map View
- Interactive map for selecting the sighting location
- Default zoom level: 0.01 latitude/longitude span
- Allows pin placement for precise location marking

### Location Type Selector
A picker/dropdown with the following options:
- Street
- Alley
- Park
- Residential
- Commercial
- Other

## Photo Section
- Photo upload capability
- Maximum of 5 photos allowed
- Gallery/file picker interface

## Colony Size Section

### Estimated Colony Size Display
- Shows calculated minimum and maximum cat count range
- Format: "X-Y cats"
- Styled with:
  - Title: "Estimated Colony Size"
  - Subtitle: "Based on your observations, we estimate there are:"
  - Count display in blue, medium weight font

### Cat Count Input
- Numeric input for "How many cats did you see?"
- Range: 1-400 cats
- Controls:
  - Decrement button (minus icon)
  - Current count display
  - Increment button (plus icon)
  - Supports both single tap and long-press for rapid adjustment

### Visibility Assessment
Title: "Visibility"
Subtitle: "How well could you see the area?"
Options (Segmented Control):
- Clear View
- Partial View
- Limited View

### Movement Assessment
Title: "Cat Movement"
Subtitle: "Were the cats moving around a lot?"
Options (Segmented Control):
- Stationary
- Some Movement
- High Movement

### Observation Time
Title: "Observation Time"
Subtitle: "How long did you observe the area?"
Options (Segmented Control):
- Brief (<5 min)
- Short (5-15 min)
- Extended (>15 min)

## Additional Details Section

### Feeding Status
- Toggle switch
- Label: "Cats Are Being Fed Here"

### Notes Field
- Multi-line text input
- Label: "Notes (optional)"
- Minimum 3 lines, maximum 6 lines

## Navigation Elements
- Title: "Add Sighting"
- Save button in navigation bar
- Cancel/dismiss option

## Form Layout
- Organized in distinct sections with headers
- Consistent spacing and padding
- Clear visual hierarchy with section headers

## Typography Guidelines
- Section Headers: Default case (not uppercase)
- Field Labels: Regular weight
- Subtitles: Gray color, caption style
- Input Values: System default
- Counts: Medium weight, blue color for emphasis

This documentation ensures consistent implementation of UI elements across both iOS and web platforms while maintaining the same user experience and data collection capabilities.
