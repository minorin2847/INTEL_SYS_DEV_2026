import type { ListingInput } from "../types";

export const PROPERTY_TYPES = [
  "Nhà riêng",
  "Căn hộ chung cư",
  "Đất",
  "Nhà mặt phố",
  "Biệt thự",
  "Nhà trọ, phòng trọ",
  "Kho, xưởng",
  "Khác",
];

export const POSITIONS = [
  "Đường chính",
  "Trong hẻm",
  "Mặt tiền",
  "Góc 2 mặt tiền",
];

export const DIRECTIONS = [
  "Đông",
  "Tây",
  "Nam",
  "Bắc",
  "Đông Nam",
  "Đông Bắc",
  "Tây Nam",
  "Tây Bắc",
];

export const ROAD_TYPES = [
  "Đường nhựa",
  "Đường bê tông",
  "Đường đất",
  "Đường rải đá",
];

export const AGENT_ROLES = [
  "Chính chủ",
  "Môi giới",
];

export const TOP_PROVINCES = [
  { slug: "tp-ho-chi-minh", label: "TP. Hồ Chí Minh" },
  { slug: "ha-noi", label: "Hà Nội" },
  { slug: "da-nang", label: "Đà Nẵng" },
  { slug: "binh-duong", label: "Bình Dương" },
  { slug: "dong-nai", label: "Đồng Nai" },
  { slug: "can-tho", label: "Cần Thơ" },
  { slug: "hai-phong", label: "Hải Phòng" },
  { slug: "an-giang", label: "An Giang" },
  { slug: "khanh-hoa", label: "Khánh Hòa" },
  { slug: "lam-dong", label: "Lâm Đồng" },
  { slug: "ba-ria-vung-tau", label: "Bà Rịa - Vũng Tàu" },
  { slug: "quang-ninh", label: "Quảng Ninh" },
  { slug: "kien-giang", label: "Kiên Giang" },
  { slug: "thanh-hoa", label: "Thanh Hóa" },
  { slug: "nghe-an", label: "Nghệ An" },
];

export interface Preset {
  id: string;
  name: string;
  description: string;
  data: ListingInput;
}

export const PRESETS: Preset[] = [
  {
    id: "rach-gia-full",
    name: "Rach Gia Townhouse",
    description: "78.7 m² townhouse, 2 floors, 3 bedrooms, asphalt road in An Giang",
    data: {
      Area: 78.7,
      Width: 4.0,
      Length: 19.6,
      Bedrooms: 3,
      Bathrooms: 2,
      Floors: 2,
      "Alley Width": 3.5,
      "Agent Listing Count": 1,
      "Property Type": "Nhà riêng",
      Position: "Đường chính",
      Direction: "Nam",
      "Road Type": "Đường nhựa",
      Province: "an-giang",
      "Agent Role": "Chính chủ",
      ward: "Phường An Hòa",
      district: "Rạch Giá",
    },
  },
  {
    id: "hcm-apartment",
    name: "District 7 Apartment (HCMC)",
    description: "65.5 m² condominium, 2 bedrooms, Southeast facing in Ho Chi Minh City",
    data: {
      Area: 65.5,
      Bedrooms: 2,
      Bathrooms: 2,
      Floors: 1,
      "Property Type": "Căn hộ chung cư",
      Position: "Đường chính",
      Direction: "Đông Nam",
      Province: "tp-ho-chi-minh",
      "Agent Role": "Môi giới",
      district: "Quận 7",
    },
  },
  {
    id: "hanoi-land",
    name: "Hanoi Residential Land",
    description: "100 m² street-front land plot, Northwest facing in Hanoi",
    data: {
      Area: 100.0,
      Width: 5.0,
      Length: 20.0,
      "Property Type": "Đất",
      Position: "Đường chính",
      Direction: "Tây Bắc",
      "Road Type": "Đường nhựa",
      Province: "ha-noi",
      "Agent Role": "Chính chủ",
      district: "Gia Lâm",
    },
  },
  {
    id: "minimal",
    name: "Minimal (Area Only)",
    description: "Only usable area (85 m²) provided; pipeline imputes omitted attributes",
    data: {
      Area: 85.0,
    },
  },
];
