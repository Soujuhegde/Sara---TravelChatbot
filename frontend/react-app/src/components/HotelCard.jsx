import React, { useState } from 'react';

const HotelCard = ({ hotel }) => {
  const [currentImageIdx, setCurrentImageIdx] = useState(0);
  const images = hotel.images && hotel.images.length > 0 ? hotel.images : [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=600&q=80"
  ];

  const handleBook = () => {
    if (hotel.onOptionSelect) {
      hotel.onOptionSelect(hotel, hotel.name, hotel.price_per_night);
    }
  };

  const nextImage = (e) => {
    e.stopPropagation();
    setCurrentImageIdx((prev) => (prev + 1) % images.length);
  };

  const prevImage = (e) => {
    e.stopPropagation();
    setCurrentImageIdx((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col md:flex-row gap-5 mt-4 p-4 w-full">
      {/* Left: Image gallery */}
      <div className="w-full md:w-64 h-48 md:h-auto min-h-[180px] rounded-2xl overflow-hidden relative group flex-shrink-0">
        <img 
          src={images[currentImageIdx]} 
          alt={hotel.name} 
          className="w-full h-full object-cover" 
        />
        {images.length > 1 && (
          <>
            <button 
              onClick={prevImage}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-black/50 hover:bg-black/75 text-white rounded-full flex items-center justify-center text-xs transition-colors"
            >
              ◀
            </button>
            <button 
              onClick={nextImage}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-black/50 hover:bg-black/75 text-white rounded-full flex items-center justify-center text-xs transition-colors"
            >
              ▶
            </button>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1 justify-center z-10">
              {images.map((_, i) => (
                <div 
                  key={i} 
                  className={`w-1.5 h-1.5 rounded-full ${i === currentImageIdx ? 'bg-white' : 'bg-white/50'}`}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Middle: Details */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-bold text-slate-800 text-xl">{hotel.name}</h3>
              <div className="flex items-center gap-1.5 my-1">
                <div className="flex text-yellow-400 text-sm">
                  {"★".repeat(Math.floor(Number(hotel.star_rating) || 3))}
                  {"☆".repeat(5 - Math.floor(Number(hotel.star_rating) || 3))}
                </div>
                <span className="text-xs font-semibold text-slate-500">{hotel.star_rating} Star</span>
              </div>
            </div>
            
            {hotel.guest_rating && (
              <div className="bg-emerald-50 text-emerald-700 font-bold px-2.5 py-1 rounded-lg text-sm border border-emerald-100 flex items-center gap-1">
                ⭐ {hotel.guest_rating}
              </div>
            )}
          </div>

          <p className="text-sm text-slate-500 my-2 font-medium flex items-center gap-1">
            📍 {hotel.distance || "Convenient location"}
          </p>

          <div className="flex flex-wrap gap-1.5 mt-3">
            {hotel.amenities && hotel.amenities.map((amenity, i) => (
              <span key={i} className="text-[11px] text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full font-medium">
                {amenity}
              </span>
            ))}
          </div>
        </div>

        <div className="flex justify-between items-center mt-5 pt-4 border-t border-slate-100">
          <div>
            <span className="text-2xl font-black text-slate-800">{hotel.price_per_night}</span>
            <span className="text-xs text-slate-500 font-medium"> / night</span>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={() => alert(`Details for ${hotel.name}: ${hotel.distance || 'Convenient location'}. Star rating: ${hotel.star_rating} Stars. Amenities: ${hotel.amenities ? hotel.amenities.join(', ') : 'N/A'}. Guest rating: ${hotel.guest_rating || 'N/A'}`)}
              className="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-bold rounded-xl hover:bg-slate-50 transition-colors"
            >
              View Details
            </button>
            <button 
              onClick={handleBook}
              className="px-5 py-2 bg-brand text-white text-sm font-bold rounded-xl hover:opacity-90 transition-opacity shadow-sm"
            >
              Book This Hotel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HotelCard;
