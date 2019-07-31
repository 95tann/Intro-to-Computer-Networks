// ************************************************************
// CS 456    : Computer Networks
// assignment: 2
// filename  : sender.java
// author    : Tanmay Shah
// ************************************************************

// import modules
import java.io.*;
import java.nio.file.*;
import java.net.*;

public class sender{

	// print error message and exit
	static void error_msg(String msg) throws Exception{
		System.out.println(msg);
		System.exit(1);
	}
    
	// fetch input from command line
	static String emulator_addr, file_name;
	static int emulator_port, sender_port;

	static void fetch_input(String args[]) throws Exception{

		// valid no. of command line args
		if (args.length == 4){
			file_name = args[3];
			sender_port = Integer.parseInt(args[2]);
			emulator_addr = args[0];
			emulator_port = Integer.parseInt(args[1]);
		}
		// invalid no. of command line args
		else{
			error_msg("Erros: Invalid no. of command line arguments");
		}
	}

	 // Global variables for sender
	static int window_size = 10;
	static int packet_max_data_len = 500;
	static int modulo = 32;
 
	// covert file contents into byte array
	static byte[] create_byte_array(String filename) throws Exception{

		File file_contents = new File(filename);
		byte[] byte_arr = null;

		// file doesn't exist so throw error msg
		if (file_contents.exists() == false){
			error_msg("Error: file not found");
		}
		// file exists
		else {
			Path filepath = Paths.get(filename);
			byte_arr = Files.readAllBytes(filepath);
		}

		return byte_arr;
	}

	// convert byte array into packet array
	static packet[] create_packet_array(byte[] bytes) throws Exception{

		double packet_data_len_d = (double) packet_max_data_len;
		double byte_arr_len = (double) bytes.length;
		int total_packets = (int)Math.ceil(byte_arr_len / packet_data_len_d);

		// iteratively create packet array 
		int i = 0;
		int bytes_converted = 0;
		packet[] packet_arr = new packet[total_packets];

		while (i < total_packets){
			byte[] packet_info;

			if (byte_arr_len <= packet_max_data_len + bytes_converted){
				int diff = ((int)byte_arr_len) - bytes_converted;
				packet_info = new byte[diff];
				System.arraycopy(bytes,bytes_converted,packet_info,0,diff);
			}
			else{
				packet_info = new byte[packet_max_data_len];
				System.arraycopy(bytes,bytes_converted,packet_info,0,packet_max_data_len);

			}

			bytes_converted = bytes_converted + packet_max_data_len;
              
            // Add new packet to packet array
            String p_str = new String(packet_info);
			packet_arr[i] = packet.createPacket(i % modulo, p_str);

			// udpate index for loop
			i = i + 1;
		}

		return packet_arr;		
	}

	// send packets to destination port of emulator IP address 
	static void send_packets(int starting_packet, int ending_packet, packet packets[], PrintWriter seqnum_writer) throws Exception{

		DatagramSocket client_socket = new DatagramSocket();
		InetAddress client_IP_adress = InetAddress.getByName(emulator_addr);
		
		// send the packet and then log seq number
		int i = starting_packet;
		while(i < ending_packet){
			// create and send datagram 
			byte to_send[] = packets[i].getUDPdata();
			DatagramPacket send_packet = new DatagramPacket(to_send, to_send.length, client_IP_adress, emulator_port);
			client_socket.send(send_packet);

			// log sequence number
			int sqnum = packets[i].getSeqNum(); 
			seqnum_writer.println(sqnum);
            
            // increment index
			i = i + 1;
		}
	}

	static DatagramSocket ack_socket = null;
	// receive acknowledgements from receiver and log sequence numbers
	static int receive_acks(PrintWriter ack_writer, int len_timeout) throws Exception{

		// set timer timeout
		try{
			ack_socket.setSoTimeout(len_timeout);
		}
		catch(SocketException e){
			e.printStackTrace();
			return -1;
		}

		// get receiving packet
		byte[] recv_info = new byte[512];
		DatagramPacket ack_packet = new DatagramPacket(recv_info, recv_info.length);

		// attempt to receive an acknowledgement
		// if timeout occurs return -1
		try{
			ack_socket.receive(ack_packet);
		}
		catch(IOException e) {
  			//ack_socket.close();
  			return -1;
		}
        
        // otherwise log and return sequence number
        packet recv_packet = null;
		try{
			recv_packet = packet.parseUDPdata(recv_info);
		}
		catch (Exception e){
			e.printStackTrace();
			return -1;
		}
        
		if (recv_packet.getType() == 0){
			// type == 0 (ACK), so log seq num
			int sqnum = recv_packet.getSeqNum();
			ack_writer.println(sqnum);
			return sqnum;
		}
		else{
			// type != 0 (not an ACK), so don't log seq num
			return recv_packet.getSeqNum();
		}
	}

	// continues to send packets to receiver until every sent packet is acknowledged
	static void keep_sending(packet[] packets, PrintWriter ack_writer, PrintWriter seqnum_writer) throws Exception{

		int start_packet = 0;
		int packets_sent_not_ack = start_packet;
		int packets_ackd = start_packet;

		while(packets.length > packets_ackd){

			// determine range of packets to send
			int starting = packets_sent_not_ack + start_packet;
			int ending = 0;
			if (packets.length < window_size + start_packet){
				ending = packets.length;
			}
			else{
				ending = window_size + start_packet;
			}

			// send packets
			send_packets(starting, ending, packets, seqnum_writer);
            
            // update variables
			int ack_so_far = 0;
			int received_ack = receive_acks(ack_writer,200);
			while (received_ack != -1){
				
				while (received_ack != ((start_packet + ack_so_far) % modulo)) {
					ack_so_far = ack_so_far + 1;
				}
				if (window_size >= ack_so_far){
					packets_ackd = packets_ackd + ack_so_far;
					start_packet = start_packet + ack_so_far;
					packets_sent_not_ack = packets_sent_not_ack - ack_so_far;
					break;
				}
				received_ack = receive_acks(ack_writer,200);
			}
			
			// didn't get ack for sent packet
			packets_sent_not_ack = 0;
		}
	}

	// main function: initiatizes sender.java program
    public static void main(String args[]) throws Exception{

		// get input from cmd line
		fetch_input(args);

		// generate packets
		byte[] byte_array = create_byte_array(file_name);
		packet[] packet_array = create_packet_array(byte_array);

		// create writers to log output
		PrintWriter seqnum_writer = new PrintWriter("seqnum.log", "UTF-8");
		PrintWriter ack_writer = new PrintWriter("ack.log", "UTF-8");

		// create socket to receive acks
		try{
			ack_socket = new DatagramSocket(sender_port);
		}
		catch (SocketException e) {
        	e.printStackTrace();
    	}

		// keep sending packets until all have been acknowledged (except EOT)
		keep_sending(packet_array, ack_writer, seqnum_writer);

		// create and send EOT packet
		packet[] eot_packet = new packet[1];
		eot_packet[0] = packet.createEOT(packet_array.length);
		send_packets(0,1,eot_packet,seqnum_writer);

		// receive final EOT from receiver 
	    int recv_eot = receive_acks(ack_writer,300);
	    while(packet_array.length != recv_eot){
	    	recv_eot = receive_acks(ack_writer,300);  // keep trying in case incorrect packet recv
	    }

	    // close writers
	    ack_writer.close();
	    seqnum_writer.close();  
	}
}
