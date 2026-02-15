export const leftCategories = [
  'Home',
  'Grocery',
  'Convenience',
  'Alcohol',
  'Health',
  'Retail',
  'Pet',
  'Flowers',
  'Baby',
  'Personal Care',
  'Electronics'
]

export const recommendations = [
  {
    title: 'Quiet Corner Cafe',
    detail: 'Great for focus sessions and late-night work.',
    tag: 'Work-friendly'
  },
  {
    title: 'Sunrise Grocery',
    detail: 'Fresh local produce with fast delivery.',
    tag: 'Fresh Picks'
  },
  {
    title: 'City Wellness',
    detail: 'Top rated for quick self-care breaks.',
    tag: 'Top Rated'
  }
]

export const categoryItems = {
  Home: [
    {
      slug: 'home-base',
      title: 'Home Base',
      category: 'Home',
      tags: ['Essentials', 'Decor'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 210,
      reviewsText: [
        'Super clean store and friendly staff.',
        'Fast checkout and helpful recommendations.'
      ],
      deliveryFee: '$4.99',
      eta: '15-25 min'
    }
  ],
  Grocery: [
    {
      slug: 'fresh-market',
      title: 'Fresh Market',
      category: 'Grocery',
      tags: ['Fresh Picks', 'Delivery'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80',
      rating: 4.7,
      reviews: 350,
      reviewsText: [
        'Fast delivery and clean produce.',
        'Friendly drivers and quick replacement when items are out.'
      ],
      deliveryFee: '$5.99',
      eta: '20-30 min'
    },
    {
      slug: 'organic-pantry',
      title: 'Organic Pantry',
      category: 'Grocery',
      tags: ['Organic', 'Local'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1506806732259-39c2d0268443?auto=format&fit=crop&w=900&q=80',
      rating: 4.5,
      reviews: 190,
      reviewsText: [
        'Quiet aisles and clean layout.',
        'Friendly staff and great local options.'
      ],
      deliveryFee: '$4.49',
      eta: '15-25 min'
    }
  ],
  Convenience: [
    {
      slug: 'quick-stop',
      title: 'Quick Stop',
      category: 'Convenience',
      tags: ['Grab & Go', 'Snacks'],
      offer: 'Night Deal',
      image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80',
      rating: 4.2,
      reviews: 120,
      reviewsText: ['Fast late-night pickup.', 'Quick and friendly service.'],
      deliveryFee: '$3.99',
      eta: '10-20 min'
    },
    {
      slug: 'city-mart',
      title: 'City Mart',
      category: 'Convenience',
      tags: ['Late Night', 'Essentials'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?auto=format&fit=crop&w=900&q=80',
      rating: 4.3,
      reviews: 90,
      reviewsText: ['Clean store and fast checkout.', 'Friendly staff.'],
      deliveryFee: '$3.49',
      eta: '12-18 min'
    }
  ],
  Alcohol: [
    {
      slug: 'bottle-house',
      title: 'Bottle House',
      category: 'Alcohol',
      tags: ['Craft Beer', 'Local'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1514361892635-eae31ddbf6d8?auto=format&fit=crop&w=900&q=80',
      rating: 4.8,
      reviews: 210,
      deliveryFee: '$6.99',
      eta: '20-30 min'
    },
    {
      slug: 'nightcap-cellars',
      title: 'Nightcap Cellars',
      category: 'Alcohol',
      tags: ['Wine', 'Giftable'],
      offer: 'Member Deal',
      image: 'https://images.unsplash.com/photo-1510626176961-4b57d4fbad03?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 140,
      deliveryFee: '$5.99',
      eta: '25-35 min'
    }
  ],
  Health: [
    {
      slug: 'wellness-pharmacy',
      title: 'Wellness Pharmacy',
      category: 'Health',
      tags: ['Supplements', 'Advice'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1580281657521-02d80b7fdd2f?auto=format&fit=crop&w=900&q=80',
      rating: 4.4,
      reviews: 180,
      deliveryFee: '$4.99',
      eta: '15-25 min'
    },
    {
      slug: 'green-care',
      title: 'Green Care',
      category: 'Health',
      tags: ['Natural', 'Wellness'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?auto=format&fit=crop&w=900&q=80',
      rating: 4.3,
      reviews: 110,
      deliveryFee: '$4.49',
      eta: '15-25 min'
    }
  ],
  Retail: [
    {
      slug: 'main-street-boutique',
      title: 'Main Street Boutique',
      category: 'Retail',
      tags: ['Fashion', 'Local'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1521335629791-ce4aec67dd47?auto=format&fit=crop&w=900&q=80',
      rating: 4.5,
      reviews: 160,
      reviewsText: ['Friendly stylists and a clean shop.', 'Quiet browsing and helpful staff.'],
      deliveryFee: '$6.99',
      eta: '20-30 min'
    },
    {
      slug: 'home-style',
      title: 'Home & Style',
      category: 'Retail',
      tags: ['Decor', 'Lifestyle'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=900&q=80',
      rating: 4.2,
      reviews: 95,
      reviewsText: ['Clean displays and friendly service.', 'Fast pickup for online orders.'],
      deliveryFee: '$5.49',
      eta: '25-35 min'
    }
  ],
  Pet: [
    {
      slug: 'paws-co',
      title: 'Paws & Co.',
      category: 'Pet',
      tags: ['Pet-Friendly', 'Grooming'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=900&q=80',
      rating: 4.7,
      reviews: 240,
      deliveryFee: '$4.99',
      eta: '15-25 min'
    },
    {
      slug: 'happy-tails',
      title: 'Happy Tails',
      category: 'Pet',
      tags: ['Treats', 'Essentials'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80',
      rating: 4.5,
      reviews: 130,
      deliveryFee: '$4.49',
      eta: '20-30 min'
    }
  ],
  Flowers: [
    {
      slug: 'bloom-studio',
      title: 'Bloom Studio',
      category: 'Flowers',
      tags: ['Fresh Bouquets', 'Gifts'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1468327768560-75b778cbb551?auto=format&fit=crop&w=900&q=80',
      rating: 4.8,
      reviews: 210,
      deliveryFee: '$6.49',
      eta: '25-35 min'
    },
    {
      slug: 'petal-lane',
      title: 'Petal Lane',
      category: 'Flowers',
      tags: ['Seasonal', 'Custom'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 150,
      deliveryFee: '$6.99',
      eta: '25-35 min'
    }
  ],
  Baby: [
    {
      slug: 'tiny-steps',
      title: 'Tiny Steps',
      category: 'Baby',
      tags: ['Baby Care', 'Nursery'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80',
      rating: 4.4,
      reviews: 105,
      deliveryFee: '$5.99',
      eta: '20-30 min'
    },
    {
      slug: 'little-sprouts',
      title: 'Little Sprouts',
      category: 'Baby',
      tags: ['Organic', 'Newborn'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=900&q=80',
      rating: 4.5,
      reviews: 90,
      deliveryFee: '$5.49',
      eta: '20-30 min'
    }
  ],
  'Personal Care': [
    {
      slug: 'glow-bar',
      title: 'Glow Bar',
      category: 'Personal Care',
      tags: ['Skincare', 'Self-care'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 150,
      deliveryFee: '$4.99',
      eta: '20-30 min'
    },
    {
      slug: 'daily-ritual',
      title: 'Daily Ritual',
      category: 'Personal Care',
      tags: ['Wellness', 'Essentials'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=80',
      rating: 4.2,
      reviews: 80,
      deliveryFee: '$4.49',
      eta: '20-30 min'
    }
  ],
  Electronics: [
    {
      slug: 'tech-hub',
      title: 'Tech Hub',
      category: 'Electronics',
      tags: ['Gadgets', 'Repairs'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
      rating: 4.3,
      reviews: 120,
      deliveryFee: '$6.99',
      eta: '25-35 min'
    },
    {
      slug: 'device-depot',
      title: 'Device Depot',
      category: 'Electronics',
      tags: ['Accessories', 'Devices'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
      rating: 4.1,
      reviews: 75,
      deliveryFee: '$6.49',
      eta: '25-35 min'
    }
  ],
  Food: [
    {
      slug: 'the-daily-page',
      title: 'The Daily Page',
      category: 'Cafe',
      tags: ['Quiet/Work-Friendly', 'Wi-Fi'],
      offer: '',
      activeCoupon: '10% off lunch combos — by Friday',
      image: 'https://images.unsplash.com/photo-1481391032119-d89fee407e44?auto=format&fit=crop&w=900&q=80',
      rating: 4.8,
      reviews: 400,
      deliveryFee: '$5.99',
      eta: '15-25 min'
    },
    {
      slug: 'brew-focus',
      title: 'Brew & Focus',
      category: 'Cafe',
      tags: ['Work-friendly', 'Coffee'],
      offer: '',
      activeCoupon: '',
      image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
      rating: 4.4,
      reviews: 190,
      deliveryFee: '$5.49',
      eta: '20-30 min'
    }
  ],
  Services: [
    {
      slug: 'glow-go-salon',
      title: 'Glow & Go Salon',
      category: 'Hair & Beauty',
      tags: ['Haircut', 'Walk-ins'],
      offer: 'New Client Deal',
      image: 'https://images.unsplash.com/photo-1500917293891-ef795e70e1f6?auto=format&fit=crop&w=900&q=80',
      rating: 4.7,
      reviews: 220,
      deliveryFee: '$7.99',
      eta: '30-40 min'
    },
    {
      slug: 'urban-trim',
      title: 'Urban Trim',
      category: 'Hair & Beauty',
      tags: ['Haircut', 'Appointment'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1514996937319-344454492b37?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 180,
      deliveryFee: '$7.49',
      eta: '30-40 min'
    }
  ],
  'Education/Public Space': [
    {
      slug: 'main-st-books',
      title: 'Main St. Books',
      category: 'Bookstore',
      tags: ['Quiet/Work-Friendly', 'Wi-Fi'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=900&q=80',
      rating: 4.9,
      reviews: 520,
      deliveryFee: '$0.00',
      eta: '5-15 min'
    },
    {
      slug: 'central-library',
      title: 'Central Library',
      category: 'Library',
      tags: ['Study Rooms', 'Quiet'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=900&q=80',
      rating: 4.8,
      reviews: 600,
      deliveryFee: '$0.00',
      eta: '5-15 min'
    }
  ],
  'Food & Drink': [
    {
      slug: 'quiet-corner-cafe',
      title: 'Quiet Corner Cafe',
      category: 'Food & Drink',
      tags: ['Quiet', 'Wi-Fi', 'Outdoor Seating'],
      offer: 'Free Item (Spend A$35)',
      image: 'https://images.unsplash.com/photo-1481391032119-d89fee407e44?auto=format&fit=crop&w=900&q=80',
      rating: 4.7,
      reviews: 900,
      deliveryFee: '$5.99',
      eta: '10-20 min'
    },
    {
      slug: 'brew-focus-fd',
      title: 'Brew & Focus',
      category: 'Food & Drink',
      tags: ['Coffee', 'Work-friendly'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
      rating: 4.5,
      reviews: 320,
      deliveryFee: '$5.49',
      eta: '15-25 min'
    }
  ],
  'Public Services': [
    {
      slug: 'public-library',
      title: 'Central Library',
      category: 'Public Services',
      tags: ['Quiet', 'Wi-Fi', 'Study Rooms'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=900&q=80',
      rating: 4.8,
      reviews: 600,
      deliveryFee: '$0.00',
      eta: '5-15 min'
    },
    {
      slug: 'community-study-hub',
      title: 'Community Study Hub',
      category: 'Public Services',
      tags: ['Workspace', 'Wi-Fi'],
      offer: '',
      image: 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=900&q=80',
      rating: 4.6,
      reviews: 210,
      deliveryFee: '$0.00',
      eta: '5-15 min'
    }
  ]
}

export const businesses = Object.values(categoryItems).flat()

export const getBusinessBySlug = (slug) =>
  businesses.find((business) => business.slug === slug)
