# CatMap Data Reference

This document provides a comprehensive overview of the data structures and information collected through the CatMap iOS app.

## User Data Structure

### Basic User Information
- `id`: Unique identifier for the user
- `username`: User's chosen username
- `email`: User's email address
- `sightingsCount`: Number of cat sightings reported by the user
- `totalCats`: Total number of cats reported across all sightings
- `lastActive`: Timestamp of user's last activity
- `joinDate`: Timestamp when user joined the platform
- `photoURL`: Optional URL to user's profile photo

## Sighting Data Structure

### Core Sighting Information
- `id`: Unique identifier for the sighting
- `userId`: ID of the user who reported the sighting
- `userEmail`: Email of the reporting user (optional)
- `userName`: Username of the reporting user (optional)
- `species`: Type of cat spotted (defaults to "cat")
- `timestamp`: When the sighting was reported
- `deviceIdentifier`: Unique identifier for the reporting device
- `isHidden`: Boolean flag to hide/show sighting

### Location Data
- `coordinate`: Geographic location of the sighting
  - `latitude`: Geographic latitude
  - `longitude`: Geographic longitude
- `userLocation`: Location of the user when reporting (optional)
  - `latitude`: User's latitude
  - `longitude`: User's longitude

### Sighting Details
- `bestCount`: Best estimate of number of cats
- `minCount`: Minimum number of cats seen
- `maxCount`: Maximum number of cats seen
- `visibleCats`: Number of cats visible at time of reporting
- `isFeeding`: Whether cats were observed feeding
- `locationType`: Type of location (default: "residential")
- `notes`: Additional observations or comments
- `uncertaintyLevel`: Confidence level in the observation (default: "medium")
- `movementLevel`: Level of cat movement observed (default: "moderate")
- `timeSpent`: Duration of observation (default: "quick")

### Media
- `photoUrls`: Comma-separated list of URLs to photos of the sighting

### Edit History
When a sighting is edited, the following information is tracked:
- `coordinate`: Updated location
- `details`: Updated sighting details
- `timestamp`: When the edit was made
- `editedBy`: User who made the edit

## Data Validation

The application performs the following validations:

### Required Fields
- Sighting ID
- User ID
- Species
- Location Type
- Valid coordinates (latitude/longitude)

### Coordinate Validation
- Latitude must be within valid range (-90 to 90)
- Longitude must be within valid range (-180 to 180)

### Data Integrity
- Duplicate sightings are prevented based on ID and coordinates
- Photo URLs are validated and stored
- All numeric counts (cats, sightings) must be non-negative

## Storage and Synchronization

The application uses:
- CoreData for local storage
- Firestore for cloud storage
- Automatic synchronization between local and cloud data
- Batch updates for maintaining data consistency
