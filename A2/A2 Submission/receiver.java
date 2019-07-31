// ************************************************************
// CS 456    : Computer Networks
// assignment: 2
// filename  : receiver.java
// author    : Tanmay Shah
// ************************************************************

// import modules
import java.io.*;
import java.net.*;

public class receiver {
    
    // print error message and exit
    static void error_msg(String msg) throws Exception{
        System.out.println(msg);
        System.exit(1);
    }

    // fetch input from command line
    static String emulator_addr, file_name;
    static int emulator_port, client_port;
    static int modulo = 32;

    static void fetch_input(String args[]) throws Exception{

        // valid no. of command line args
        if (args.length == 4){
            file_name = args[3];
            client_port = Integer.parseInt(args[2]);
            emulator_addr = args[0];
            emulator_port = Integer.parseInt(args[1]);
        }
        // invalid no. of command line args
        else{
            error_msg("Erros: Invalid no. of command line arguments");
        }
    }

    // sends acknowledgements for packets received
    static void acknowledge_packet(packet p, DatagramSocket s) throws Exception{
        InetAddress ip_addr = InetAddress.getByName(emulator_addr);
        byte[] ack_data = p.getUDPdata();
        DatagramPacket send_packet = new DatagramPacket(ack_data, ack_data.length, ip_addr, emulator_port);
        s.send(send_packet);
    }

    // receive incoming packets and accordingly sends acknowledgements
    static void receive_packets(PrintWriter seqnum_writer, PrintWriter output_file_writer) throws Exception{
        // Create sockets
        DatagramSocket svr_socket = new DatagramSocket(client_port);
        DatagramSocket ack_socket = new DatagramSocket();

        // other variables needed
        byte[] recv_info = new byte[1024];
        int starting_packet = 0; 
        int packet_sqnum = starting_packet;
        int expect_sqnum = packet_sqnum;
        boolean eot_received = false;

        while(eot_received == false){
            // remove data from recv packet
            DatagramPacket recv_packet = new DatagramPacket(recv_info, recv_info.length);
            svr_socket.receive(recv_packet);
            packet recv_packet_data = packet.parseUDPdata(recv_packet.getData());

            // write seq number
            int sqnum = recv_packet_data.getSeqNum();
            seqnum_writer.println(sqnum);

            // deal with in-order & out-of-order packets
            if (sqnum == expect_sqnum){
                // update output file as long as type not EOT
                if(1 == recv_packet_data.getType()){
                    String data = new String(recv_packet_data.getData());
                    output_file_writer.print(data);
                }

                // this is an in-order packet, so modify variables
                packet_sqnum = expect_sqnum;                              
                expect_sqnum = (expect_sqnum + 1) % modulo;  
                starting_packet = 1;          // recv first packet
                
            }
            else if (sqnum != expect_sqnum && starting_packet != 0){
                // received incorrect packet, modify to last ACK seq num
                packet_sqnum = expect_sqnum % modulo;
            }
            else{
                // still waiting for receipt of first packet, so skip this packet and restart loop
                continue;
            }

            if (recv_packet_data.getType() != 1){
                // EOT received
                eot_received = true;
            }
            if (recv_packet_data.getType() == 1){

                 // now let's create and send packet acknowledgement 
                 packet ack_packet = packet.createACK(packet_sqnum);  
                 acknowledge_packet(ack_packet, ack_socket);             
            }
        }

        // send final EOT
        packet eot_packet = packet.createEOT(packet_sqnum);
        acknowledge_packet(eot_packet, ack_socket);
    }

    public static void main(String[] args) throws Exception{

        // get input from cmd line
        fetch_input(args);

        // create writers to log output
        PrintWriter seqnum_writer = new PrintWriter("arrival.log", "UTF-8");
        PrintWriter output_file_writer = new PrintWriter(file_name, "UTF-8");
 
        // deal with incoming packets
        receive_packets(seqnum_writer, output_file_writer);

        // close writers
        seqnum_writer.close();
        output_file_writer.close();
    }

}
