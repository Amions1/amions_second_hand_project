// Type definitions for goodsActions.js
declare module '@/utils/goodsActions' {
  // 定义商品信息类型
  interface GoodsItem {
    id: number;
    title: string;
    price: number;
    image: string;
    quality?: string;
    status: number;
    publisher_id: bigint;
    publisher_nickname?: string;
  }
  
  interface LoadFunctions {
    loadPublishedGoods: (userId: string) => Promise<void>;
    loadBoughtGoods: (userId: string) => Promise<void>;
    loadOffShelfGoods: (userId: string) => Promise<void>;
    loadSoldGoods: (userId: string) => Promise<void>;
    loadWishlistGoods: (userId: string) => Promise<void>;
  }
  
  export const takeDownOrPutDownGoods: (
    goods: GoodsItem,
    activeSubNav: string,
    loadFunctions: LoadFunctions
  ) => Promise<void>;
}