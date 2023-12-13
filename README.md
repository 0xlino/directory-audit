# directory-audit

# Directory Audit Script

This script performs various operations related to auditing and managing directories. It utilizes Supabase for storage and auditing purposes.

## Functions

1. **`check_if_directory_exists(directory_name)`**: 
   - Checks if a directory exists.

2. **`read_directory(path, ignores=['.git', '.DS_Store'])`**: 
   - Reads the contents of a directory, excluding specified files and directories.

3. **`create_directory_audit(directory, ignores=['.git', '.DS_Store'])`**: 
   - Creates an audit of a directory by reading its contents.

4. **`check_if_audit_exists_on_supbase(supaClient)`**: 
   - Checks if an audit exists on Supabase.

5. **`create_zip_of_directory(directory_name)`**: 
   - Creates a zip file of a directory.

6. **`create_password_protected_zip_of_directory(directory_name)`**: 
   - [TO BE IMPLEMENTED] Creates a password-protected zip file of a directory.

7. **`upload_zip_to_supabase(supaClient, directory_name)`**: 
   - Uploads a zip file to Supabase storage.

8. **`get_audit_from_supabase(supaClient, directory_name)`**: 
   - Retrieves an audit from Supabase.

9. **`save_json_pretty(directory_name, output)`**: 
   - Saves JSON output to a file in a pretty format.

10. **`download_zip_from_supabase(supaClient, directory_name)`**: 
    - Downloads a zip file from Supabase storage.

11. **`extract_zip_to_directory(directory_name)`**: 
    - Extracts the contents of a zip file to a directory.

12. **`open_and_extract_the_supabase_zip(directory_name)`**: 
    - Downloads and extracts the contents of a zip file from Supabase.

## Usage

1. Run the script, providing the directory name when prompted.
2. The script checks if the directory exists, creates a zip file, uploads it to Supabase, performs an audit, and saves the results to a JSON file.

**Note**: Some functions are marked as [TO BE IMPLEMENTED] and require further development.

Enjoy auditing and managing your directories with this script!
