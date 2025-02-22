CREATE TABLE IF NOT EXISTS audio_files (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    bytes BLOB NOT NULL,
    processing_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stitched_audio (
    id TEXT PRIMARY KEY,
    audio_file_id TEXT NOT NULL,
    generated_ad_id TEXT NOT NULL,
    audio_bytes BLOB,
    processing_status TEXT NOT NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id),
    FOREIGN KEY (generated_ad_id) REFERENCES generated_ads(id)
);

CREATE TABLE IF NOT EXISTS transcription_segments (
    id TEXT PRIMARY KEY,
    audio_file_id TEXT NOT NULL,
    no INTEGER NOT NULL,
    start REAL NOT NULL,
    end REAL NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id)
);

CREATE TABLE IF NOT EXISTS advertisements (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS generated_ads (
    id TEXT PRIMARY KEY,
    segue TEXT NOT NULL,
    content TEXT NOT NULL,
    exit TEXT NOT NULL,
    audio_bytes BLOB NOT NULL,
    audio_file_id TEXT NOT NULL,
    processing_status TEXT NOT NULL,
    transcription_segment_id TEXT NOT NULL,
    advertisement_id TEXT NOT NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id),
    FOREIGN KEY (transcription_segment_id) REFERENCES transcription_segments(id),
    FOREIGN KEY (advertisement_id) REFERENCES advertisements(id)
);

INSERT INTO advertisements (id, url, title, content, tags) VALUES 
('94043886-b0d0-484e-92fc-730569e66e43', 'https://www.dominos.co.in/', '30-Minute Delivery Guarantee', 'One of the standout features that Domino''s Pizza can advertise is their 30-minute delivery guarantee. This promise ensures that customers receive their orders swiftly, making it an ideal choice for those who want a quick and convenient meal. With over 1,250 stores across India, Domino''s has established a robust delivery network that allows them to fulfill this commitment, even offering pizza delivery on trains. This service is particularly appealing to busy individuals and families who value speed and reliability. By highlighting this guarantee in advertisements, Domino''s can attract customers looking for a fast food option without compromising on quality.', 'pizza,delivery'),

('50e57529-911e-40fe-b87c-d2889a4a8126', 'https://www.chess.com/', 'Play Chess Online with Friends or Bots', 'Chess.com offers a variety of ways to play chess online. You can challenge friends or play against customizable training bots to improve your skills. The platform also provides real-time games with players from around the world, ensuring a dynamic and engaging experience. Whether you''re a beginner or an experienced player, Chess.com has something to offer.', 'test'),

('cd391b86-b472-464c-9edd-f43c48ee5940', 'https://www.dominos.co.in/store-locations/', 'Domino''s Pizza: The Best Pizza Experience Near You', 'Domino''s Pizza is renowned for its delicious pizzas and exceptional service. Whether you''re in the mood for a quick lunch or a late-night snack, Domino''s has you covered. With a wide variety of pizzas, pasta, and sides, you can customize your meal to your liking. Plus, their delivery service is fast and reliable, ensuring that your food arrives hot and fresh. Don''t miss out on the chance to try Domino''s Pizza today!', 'pizza, delivery'),

('76bea6de-6098-4cc2-9a39-ac6a7c7b13d9', 'https://www.dominos.co.in/menu', 'Domino''s Pizza Menu Highlights', 'Discover the delightful world of Domino''s Pizza with our extensive menu. From classic favorites like the Margherita and Farmhouse to tantalizing options like the Chicken Fiesta and Non-Veg Supreme, there''s something for every taste. Don''t forget to explore our Pizza Mania range for a mouth-watering experience. Additionally, complement your pizza with a variety of sides and beverages, including garlic bread, roasted chicken wings, and refreshing drinks. Check out our menu for more details and place your order today!', 'pizza, delivery'),

('ca558fc1-4a7e-46e0-8f7c-5bccf341e710', 'https://www.dominos.co.in/gift-vouchers', 'Domino''s Pizza Gift Vouchers: Perfect for Any Occasion', 'Domino''s Pizza Gift Vouchers are an excellent choice for any occasion, whether it''s a birthday, anniversary, or a festive celebration. These vouchers can be redeemed online or at any Domino''s Pizza outlet, making it convenient for the recipient to enjoy a delicious meal. The vouchers come in various denominations and can be customized to suit the recipient''s preferences. Additionally, Domino''s offers exciting deals and offers on their gift vouchers, making them an affordable and thoughtful gift option.', 'pizza, delivery'),

('b3294de8-9032-4fff-94bd-af5cbdc1e16f', 'https://swissbeauty.in/', 'Swiss Beauty: Your Ultimate Destination for High-Quality Makeup and Skincare', 'Swiss Beauty is a leading brand in the beauty and cosmetics industry, offering a wide range of innovative and high-quality products. From makeup kits to skincare essentials, Swiss Beauty caters to all your beauty needs. With a focus on quality and innovation, Swiss Beauty ensures that every product is safe, effective, and long-lasting. Whether you are looking for a perfect makeup kit for everyday use or a luxurious skincare set for special occasions, Swiss Beauty has something for everyone. The brand is committed to providing the best products at affordable prices, making it a go-to destination for all beauty enthusiasts.', 'beauty, women'),

('80e8b000-b1d0-4825-8c29-540f4bd56f9a', 'https://www.lego.com/en-in', 'LEGO® Botanicals Pretty Pink Flower Bouquet', 'Spark joy with the new LEGO® Botanicals Pretty Pink Flower Bouquet. This stunning set is perfect for adding a touch of elegance to any space. Whether you''re looking to brighten up your home or give a thoughtful gift, this artificial flower bouquet is sure to delight. Shop now to bring a pop of color to your life.', 'toys, kids, men'),

('a71d4714-acf8-4c97-b7b8-b1e5c3a314d4', 'https://www.lego.com/en-in/themes', 'LEGO® Animal Crossing™', 'Take your Animal Crossing™ play to the next level as you invent adventures for the characters from the video game series. Build their homes then endlessly customise them, inside and out, any way you like! Shop Products', 'toys, kids, men'),

('673e8be9-5d52-452a-9e97-c91f408f1489', 'https://www.lego.com/en-in/categories/all-sets', 'Venator-Class Republic Attack Cruiser™', 'Experience the thrill of the galaxy with the Venator-Class Republic Attack Cruiser™. This 18+ set features 5374 pieces and is perfect for fans of Star Wars. Build and display this iconic spaceship, complete with detailed design and authentic colors. Ideal for both collectors and builders, this set offers a challenging and rewarding build experience.', 'toys, kids, men'),

('d986c8f3-23a1-4849-ac77-431f9412ae4f', 'https://swissbeauty.in/collections/face-foundation', 'Discover the Perfect Foundation for Your Skin with Swiss Beauty', 'Swiss Beauty offers a wide range of foundations designed to cater to every skin type and tone. Whether you have oily, dry, or combination skin, our collection includes lightweight, long-lasting formulas that provide a smooth, even finish. Our foundations are formulated with care, using high-quality ingredients that are gentle on your skin. With a variety of shades available, you can find your perfect match, no matter your skin tone. Shop our extensive collection of foundations online and enjoy exclusive offers and discounts.', 'women, beauty, skin, face');
