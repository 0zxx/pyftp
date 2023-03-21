import paramiko

# definir as configurações do servidor
host = 'seu_host'
port = 22
username = 'seu_usuario'
password = 'sua_senha'

# conectar ao servidor SFTP
transport = paramiko.Transport((host, port))
transport.connect(username=username, password=password)

# criar cliente SFTP
sftp = paramiko.SFTPClient.from_transport(transport)

# fazer upload de um arquivo para o servidor
local_file_path = 'caminho/do/arquivo/local'
remote_file_path = 'caminho/do/arquivo/remote'
sftp.put(local_file_path, remote_file_path)

# fazer download de um arquivo do servidor
local_file_path = 'caminho/do/arquivo/local'
remote_file_path = 'caminho/do/arquivo/remote'
sftp.get(remote_file_path, local_file_path)

# renomear um arquivo no servidor
old_remote_file_path = 'caminho/do/arquivo/antigo'
new_remote_file_path = 'caminho/do/arquivo/novo'
sftp.rename(old_remote_file_path, new_remote_file_path)

# excluir um arquivo do servidor
remote_file_path = 'caminho/do/arquivo'
sftp.remove(remote_file_path)

# desconectar do servidor SFTP
sftp.close()
transport.close()
