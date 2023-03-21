import argparse
import ftplib
import hashlib
import base64
import base32_crockford
import base58

# Define the command-line arguments
parser = argparse.ArgumentParser(description='FTP client to list directories, delete files, download files, upload files, and rename files.')
parser.add_argument('--server', required=True, help='FTP server address')
parser.add_argument('--username', required=True, help='FTP username')
parser.add_argument('--password', required=True, help='FTP password')
parser.add_argument('--list', metavar='DIRECTORY', help='List directories')
parser.add_argument('--delete', metavar='FILE', help='Delete file')
parser.add_argument('--download', metavar='FILE', help='Download file')
parser.add_argument('--upload', metavar=('LOCAL_FILE', 'REMOTE_FILE'), nargs='+', help='Upload file and optionally rename it')
parser.add_argument('--hash', required=False, help='Hash sequence (e.g. base64+base32+base58)')

# Parse the command-line arguments
args = parser.parse_args()

# Check if there are existing credentials
if args.hash:
    hash_sequence = args.hash.split('+')
else:
    hash_sequence = []

if len(hash_sequence) == 0:
    use_existing = input('Existing credentials found. Do you want to use them? (y/n): ').lower() == 'y'
else:
    use_existing = False

if use_existing:
    os.system('gpg -d credentials.gpg > credentials.txt')
    with open('credentials.txt', 'r') as f:
        encrypted_username = f.readline().strip()
        encrypted_password = f.readline().strip()
    os.remove('credentials.txt')
    decrypted_username, decrypted_password = decrypt_credentials(encrypted_username, encrypted_password, hash_sequence)
    args.username = decrypted_username
    args.password = decrypted_password
else:
    username = input('Enter username: ')
    password = input('Enter password: ')
    encrypted_username, encrypted_password = encrypt_credentials(username, password, hash_sequence)
    with open('credentials.gpg', 'wb') as f:
        f.write(encrypted_username)
        f.write(encrypted_password)
    print('New credentials created successfully')

def encrypt_credentials(username, password, hash_sequence):
    for hash_type in hash_sequence:
        if hash_type == 'base64':
            username = base64.b64encode(username.encode()).decode()
            password = base64.b64encode(password.encode()).decode()
        elif hash_type == 'base32':
            username = base64.b32encode(username.encode()).decode()
            password = base64.b32encode(password.encode()).decode()
        elif hash_type == 'base58':
            username = base58.b58encode(username.encode()).decode()
            password = base58.b58encode(password.encode()).decode()

    # Encrypt the credentials using GPG
    with open('credentials.gpg', 'wb') as f:
        subprocess.run(['gpg', '--symmetric', '--cipher-algo', 'AES256', '-o', '-', '<<<', '{}\n{}'.format(username, password)], stdout=f)

    # Replace the original credentials file with the encrypted one
    os.replace('credentials.gpg', 'credentials')

def decrypt_credentials(hash_sequence):
    # Ask the user which hash sequence was used
    sequence_str = ' + '.join(hash_sequence)
    response = input(f"Please enter the hash sequence used to encrypt the credentials file ({sequence_str}): ")
    user_hash_sequence = response.strip().split(' + ')

    # Make sure the user entered the correct sequence
    if user_hash_sequence != hash_sequence:
        print('Invalid hash sequence.')
        return None, None

    # Decrypt the credentials file
    with open('credentials', 'rb') as f:
        subprocess.run(['gpg', '--decrypt'], stdin=f, stdout=subprocess.PIPE)

    # Decode the credentials and return them
    credentials = stdout.decode().strip().split('\n')
    return credentials[0], credentials[1]

# Connect to the FTP server
ftp = ftplib.FTP(args.server)
ftp.login(args.username, args.password)

# Perform the requested operation
if args.list:
    ftp.cwd(args.list)
    directories = ftp.nlst()
    print(directories)
elif args.delete:
    ftp.delete(args.delete)
elif args.download:
    with open(args.download, 'wb') as f:
        ftp.retrbinary('RETR {}'.format(args.download), f.write)
elif args.upload:
    local_file = args.upload[0]
    remote_file = args.upload[1] if len(args.upload) > 1 else local_file
    with open(local_file, 'rb') as f:
        ftp.storbinary('STOR {}'.format(remote_file), f)
    print('File uploaded successfully')

# Close the FTP connection
ftp.quit()
