# threadsrecon GUI - Manual Test Plan

Comprehensive test scenarios to verify GUI functionality and error handling.

## Prerequisites for Testing
- Fresh installation of threadsrecon
- Valid settings.yaml configuration
- Test usernames for scraping
- Backup of original data/ directory

---

## Test Scenarios

### 1. Environment Validation

**Test 1.1: All Prerequisites Present**
- Start GUI with chromedriver and wkhtmltopdf installed
- **Expected**: All three status indicators show green checkmarks
- **Expected**: Run button is enabled
- **Expected**: Version info displayed in sidebar

**Test 1.2: Missing ChromeDriver**
- Rename or remove chromedriver binary
- Restart GUI
- **Expected**: ChromeDriver shows red X with "ChromeDriver Missing"
- **Expected**: Run button is disabled
- **Expected**: Version shows "Not Found"

**Test 1.3: Missing wkhtmltopdf**
- Remove wkhtmltopdf binary
- Restart GUI
- **Expected**: wkhtmltopdf shows red X
- **Expected**: Run button remains disabled
- **Expected**: Other checks still show correct status

**Test 1.4: Data Directory Permission Issues**
- Change data/ directory to read-only: `chmod 444 data/`
- Restart GUI
- **Expected**: "Permission Denied" red X displayed
- **Expected**: Run button disabled
- Restore permissions: `chmod 755 data/`

### 2. Settings Management

**Test 2.1: Load Valid YAML**
- Ensure valid settings.yaml exists
- Open Settings tab
- **Expected**: YAML content loaded in text area
- **Expected**: "✅ Valid YAML" indicator shown
- **Expected**: Save button available

**Test 2.2: Edit and Save Valid YAML**
- Modify a simple field (e.g., timeout value)
- Click Save button
- **Expected**: "Settings saved successfully!" message
- **Expected**: File updated on disk
- **Expected**: Changes persist after reload

**Test 2.3: Invalid YAML Syntax**
- Edit YAML to include syntax error (e.g., unmatched brackets)
- Observe validation indicator
- **Expected**: "❌ Invalid YAML: [error message]" shown
- **Expected**: Save button blocks with error message
- Fix syntax and verify indicator turns green

**Test 2.4: Missing Settings File**
- Delete settings.yaml file
- Restart GUI
- **Expected**: Empty/default YAML content loaded
- **Expected**: No crash or error
- Create new valid YAML and save

### 3. Username Management

**Test 3.1: Username Patching**
- Enter "testuser1, testuser2, testuser3" in username field
- Click Run Pipeline (with valid environment)
- **Expected**: settings.yaml updated with usernames list
- **Expected**: ScraperSettings.usernames contains ["testuser1", "testuser2", "testuser3"]
- **Expected**: Other YAML sections remain unchanged

**Test 3.2: Empty Username Input**
- Leave username field empty
- Run pipeline
- **Expected**: No YAML modification
- **Expected**: Pipeline uses existing usernames from YAML

**Test 3.3: Username with Special Characters**
- Enter "user.name, user_123, user-test"
- Run pipeline
- **Expected**: All variations preserved correctly in YAML
- **Expected**: No parsing errors

### 4. Pipeline Execution

**Test 4.1: Successful Scrape Stage**
- Set stage to "scrape"
- Enable headless mode
- Enter valid username
- Click Run Pipeline
- **Expected**: "🔄 Pipeline is running..." message
- **Expected**: Live logs appear within 1 second
- **Expected**: Stop button available during execution
- **Expected**: Success message on completion (exit code 0)

**Test 4.2: Headless Mode Toggle**
- Disable "Run in Background" checkbox
- Run scrape stage
- **Expected**: THREADSRECON_HEADLESS=0 in environment
- **Expected**: Browser window visible during execution
- Enable headless and verify browser hidden

**Test 4.3: All Stages Pipeline**
- Select "all" stage
- Run with valid configuration
- **Expected**: All stages execute in sequence
- **Expected**: Progress visible in logs
- **Expected**: Multiple artifact types generated

**Test 4.4: Invalid Stage Handling**
- Modify main.py to expect invalid stage
- **Expected**: Error message in logs
- **Expected**: Non-zero exit code displayed
- **Expected**: "❌ Pipeline failed" status

**Test 4.5: Stop Pipeline Mid-Execution**
- Start long-running stage (e.g., "all")
- Click Stop button after 10 seconds
- **Expected**: Process terminates
- **Expected**: Return to ready state
- **Expected**: Partial logs retained

### 5. Log Streaming Performance

**Test 5.1: Real-time Log Latency**
- Run scrape stage with verbose output
- Monitor log appearance timing
- **Expected**: New log lines appear within 1 second of generation
- **Expected**: No blocking of UI during execution
- **Expected**: Logs update continuously, not in batches

**Test 5.2: Large Log Volume**
- Run analyze stage with large dataset
- **Expected**: GUI remains responsive
- **Expected**: Log area scrolls correctly
- **Expected**: No memory issues with long logs

### 6. Artifact Preview

**Test 6.1: JSON Artifact Display**
- Run pipeline to generate profiles.json
- Open Artifacts tab
- **Expected**: JSON files listed under "📄 JSON Data"
- **Expected**: Expandable sections for each JSON file
- **Expected**: Proper JSON formatting and syntax highlighting

**Test 6.2: Image Gallery**
- Run visualization stage
- Check Artifacts tab
- **Expected**: Images appear under "🖼️ Visualizations"
- **Expected**: Images display correctly with captions
- **Expected**: Three-column layout maintained

**Test 6.3: PDF Report Links**
- Run report stage
- Check Artifacts tab
- **Expected**: PDF listed under "📋 Reports"
- **Expected**: "📖 Open" button available
- **Expected**: File path displayed when clicked

**Test 6.4: Empty Artifacts State**
- Clear data/ directory
- Refresh Artifacts tab
- **Expected**: "No JSON artifacts found" message
- **Expected**: "No visualization images found" message
- **Expected**: "No PDF reports found" message

### 7. Error Handling

**Test 7.1: Corrupted JSON Artifacts**
- Create invalid JSON file in data/
- Open Artifacts tab
- **Expected**: "Failed to load JSON file" error for corrupted file
- **Expected**: Other valid files still display correctly

**Test 7.2: Missing Image Files**
- Create broken image symlink in data/visualizations/
- Open Artifacts tab
- **Expected**: "Failed to load [filename]" error for broken image
- **Expected**: Other images display normally

**Test 7.3: Permission Denied During Execution**
- Make data/ read-only during pipeline execution
- **Expected**: Error in logs about write permissions
- **Expected**: Pipeline fails gracefully
- **Expected**: Clear error message to user

### 8. Data Persistence

**Test 8.1: Settings Persistence**
- Edit YAML settings
- Save changes
- Restart GUI
- **Expected**: Saved settings loaded correctly
- **Expected**: No data loss

**Test 8.2: Log Retention**
- Run pipeline to completion
- Switch between tabs
- Return to Run tab
- **Expected**: Final logs still displayed
- **Expected**: Success/failure status preserved

### 9. UI Responsiveness

**Test 9.1: Concurrent Tab Usage**
- Start pipeline execution
- Switch to Settings tab while running
- Edit and save YAML
- Return to Run tab
- **Expected**: No interference between tabs
- **Expected**: All operations complete successfully

**Test 9.2: Browser Refresh During Execution**
- Start pipeline
- Refresh browser page
- **Expected**: Pipeline continues running
- **Expected**: New session shows appropriate state
- **Expected**: No process orphaning

### 10. Docker Environment

**Test 10.1: Docker GUI Launch**
- Run `docker-compose up threadsrecon-gui`
- Access http://localhost:8501
- **Expected**: GUI loads correctly
- **Expected**: Environment checks pass
- **Expected**: All features functional

**Test 10.2: Volume Mount Persistence**
- Create settings via Docker GUI
- Restart container
- **Expected**: Settings persist
- **Expected**: Generated artifacts retained

---

## Performance Benchmarks

- **GUI startup time**: < 5 seconds
- **Log streaming latency**: < 1 second
- **YAML save operation**: < 100ms
- **Artifact refresh**: < 2 seconds
- **Environment validation**: < 3 seconds

## Test Environment Cleanup

After each test run:
1. Restore original settings.yaml
2. Clear data/ directory: `rm -rf data/*`
3. Reset file permissions: `chmod 755 data/`
4. Verify no background processes remain

## Critical Issues to Report

- GUI unresponsive for >30 seconds
- Data corruption or loss
- Security credential exposure
- Process memory leaks
- Cross-site scripting vulnerabilities
- Unhandled exceptions causing crashes