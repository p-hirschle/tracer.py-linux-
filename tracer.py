import socket
import struct
import sys

def main(dest_name):
    dest_addr = socket.gethostbyname(dest_name) // puxar ip do host
    port = 33434 // porta comumente associada à tracers
    max_hops = 30 // num máximo de roteadores a serem percorridos
    icmp = socket.getprotobyname('icmp') // puxar constante do protocolo
    udp = socket.getprotobyname('udp') // puxar constante do protocolo
    ttl = 1 // time to live do pacote
    
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) #define socket receptor como ipv4, raw e icmp
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp) #define socket enviador como ipv4, raw e udp
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        timeout = struct.pack("ll", 3, 0)

        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout) #SOL_SOCKET torna o socket independente de protocolo, SO_RCVTIMEO define o tempo de timeout do socket

        recv_socket.bind(("", port))
        sys.stdout.write(" %d  " % ttl)
        send_socket.sendto(b"", (dest_name, port)) #manda pacote para o endereço de destino
        curr_addr = None
        curr_name = None
        finished = False
        tries = 3
        while not finished and tries > 0:
            try:
                _, curr_addr = recv_socket.recvfrom(512) #recebe o endereço ip do roteador atual de acordo com o TTL
                finished = True
                curr_addr = curr_addr[0] 
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0] #procura o nome do host pelo endereço
                except socket.error:
                    curr_name = curr_addr
            except socket.error as err: #ao acontecer erro imprime *** na tela
                tries = tries - 1
                sys.stdout.write("* ")

        send_socket.close() #fecha os dois sockets ao receber o pacote de resposta
        recv_socket.close()

        if not finished:
            pass

        if curr_addr is not None: #imprimir o endereço atual
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = ""
        sys.stdout.write("%s\n" % (curr_host))

        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:  
            break


if __name__ == "__main__":
    main('poli.br')
