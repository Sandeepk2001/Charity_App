// SPDX-License-Identifier: MIT               # SPDX is a standard way for communicating the terms of a software license
pragma solidity ^0.8.0;                      

contract Event {
    

    struct eventDetails {
        
        
        string bname;
        string date;
        string baccountAddress;
        string amount;
        string caccountAddress;
    }

    eventDetails[] public EventDetails; 
     
   
    function getEventDetails() public view returns (eventDetails[] memory){
        return EventDetails; 
    }

    function addEventDetails(string memory _bname ,string memory _date,string memory _baccount,string memory _amount,string memory _caccount) public {
        EventDetails.push(eventDetails(_bname, _date,_baccount,_amount,_caccount)); //append to  Contact[] array
       
    }


    
}


contract EventDonation{

    struct Donation {
        
        string fromName;
        string toName; //charity name
        string date;
        string accountAddress;
        string amount;
 
    }
    
    Donation[] public donationDetails; 

    function getDonationDetails() public view returns (Donation[] memory){
        return donationDetails; 
    }

    function addDonationDetails(string memory _fromName ,string memory _toName,string memory _date,string memory _account,string memory _amount) public {
        donationDetails.push(Donation(_fromName, _toName,_date,_account,_amount)); //append to  Contact[] array
       
    }



}


contract DonationTracking{

    struct Track {
        
        string bName;
        string fName; //charity name
        string date;
        string accountAddress;
        string amount;
 
    }

       

    Track[] public trackingDetails; 

    function getTrackingDetails() public view returns (Track[] memory){
        return trackingDetails; 
    }

    function addTrackingDetails(string memory _bName ,string memory _fName,string memory _date,string memory _account,string memory _amount) public {
        trackingDetails.push(Track(_bName, _fName,_date,_account,_amount)); //append to  Contact[] array
       
    }

}

