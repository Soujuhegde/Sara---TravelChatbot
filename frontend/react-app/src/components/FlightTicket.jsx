import React from 'react';

const FlightTicket = ({ ticket }) => {
  if (!ticket) return null;

  return (
    <div className="w-full max-w-2xl mx-auto my-6 bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] overflow-hidden flex flex-col md:flex-row relative font-sans">
      
      {/* Left Section - Main Details */}
      <div className="flex-1 p-6 md:p-8 relative">
        <div className="flex justify-between items-start mb-8">
          <div>
            <span className="inline-block px-3 py-1 bg-brand-light text-brand-orange text-xs font-bold uppercase tracking-wider rounded-full mb-2">
              Boarding Pass
            </span>
            <h2 className="text-2xl font-bold text-gray-800 tracking-tight">{ticket.airline}</h2>
            <p className="text-sm text-gray-500 font-medium">{ticket.flight_class} Class</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-400 uppercase tracking-widest mb-1">PNR</p>
            <p className="text-2xl font-mono font-bold text-gray-800 tracking-wider">{ticket.pnr}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-8 relative">
          <div className="text-center">
            <p className="text-4xl font-bold text-gray-800 mb-1">{ticket.origin}</p>
            <p className="text-xs text-gray-500 uppercase font-medium">Origin</p>
          </div>
          
          <div className="flex-1 px-4 flex items-center justify-center relative">
            <div className="w-full h-[2px] bg-gray-200 border-dashed border-t-2 border-gray-300 absolute"></div>
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center z-10 border-2 border-gray-100 shadow-sm text-brand-orange transform rotate-45">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M22 2 11 13"></path><path d="m22 2-7 20-4-9-9-4Z"></path></svg>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-4xl font-bold text-gray-800 mb-1">{ticket.destination}</p>
            <p className="text-xs text-gray-500 uppercase font-medium">Destination</p>
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">Passengers</p>
          <div className="space-y-2">
            {ticket.passengers.map((p, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-800">{p.name || 'N/A'}</span>
                <span className="text-gray-500 font-mono text-xs">PP: {p.passport || 'N/A'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="hidden md:flex flex-col items-center justify-center relative w-8">
        <div className="absolute top-0 bottom-0 w-[2px] border-l-2 border-dashed border-gray-200"></div>
        <div className="w-8 h-8 bg-brand-light rounded-full absolute -top-4 shadow-inner"></div>
        <div className="w-8 h-8 bg-brand-light rounded-full absolute -bottom-4 shadow-inner"></div>
      </div>

      {/* Right Section - Tear off */}
      <div className="w-full md:w-64 bg-gradient-to-br from-brand-orange to-[#ff7a33] p-6 md:p-8 text-white flex flex-col justify-between relative overflow-hidden">
        <div className="relative z-10">
          <p className="text-white/80 text-xs uppercase tracking-widest mb-1">Total Paid</p>
          <p className="text-3xl font-bold mb-6">{ticket.price}</p>
          
          <div className="space-y-4">
            <div>
              <p className="text-white/70 text-xs uppercase tracking-wider mb-1">Date</p>
              <p className="font-semibold">{ticket.date}</p>
            </div>
            <div>
              <p className="text-white/70 text-xs uppercase tracking-wider mb-1">Flight</p>
              <p className="font-semibold">{ticket.airline}</p>
            </div>
          </div>
        </div>
        
        {/* Fake Barcode */}
        <div className="mt-8 relative z-10 opacity-90 mix-blend-overlay">
           <svg className="w-full h-12" preserveAspectRatio="none" viewBox="0 0 100 100">
             {[...Array(20)].map((_, i) => (
               <rect key={i} x={i * 5 + (Math.random() * 2)} y="0" width={Math.random() * 3 + 1} height="100" fill="currentColor" />
             ))}
           </svg>
        </div>
        
        {/* Decorative circle */}
        <div className="absolute -bottom-16 -right-16 w-48 h-48 bg-white/10 rounded-full blur-2xl"></div>
      </div>
    </div>
  );
};

export default FlightTicket;
