import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import Icon from '@/components/ui/icon';

interface Product {
  id: number;
  name: string;
  category: 'game' | 'currency';
  price: number;
  discount?: number;
  image: string;
  popular: boolean;
}

interface Purchase {
  id: number;
  product: string;
  date: string;
  amount: number;
}

const products: Product[] = [
  { id: 1, name: 'Valorant Points', category: 'currency', price: 499, discount: 20, image: '🎮', popular: true },
  { id: 2, name: 'Fortnite V-Bucks', category: 'currency', price: 599, image: '⚡', popular: true },
  { id: 3, name: 'CS2 Prime Status', category: 'game', price: 1299, discount: 15, image: '🔫', popular: true },
  { id: 4, name: 'Genshin Impact Кристаллы', category: 'currency', price: 799, image: '💎', popular: false },
  { id: 5, name: 'Minecraft Java', category: 'game', price: 2499, image: '⛏️', popular: true },
  { id: 6, name: 'Robux', category: 'currency', price: 399, discount: 10, image: '🤖', popular: true },
  { id: 7, name: 'League of Legends RP', category: 'currency', price: 499, image: '⚔️', popular: false },
  { id: 8, name: 'Steam Gift Card', category: 'currency', price: 1000, image: '🎁', popular: true },
];

export default function Index() {
  const [activeTab, setActiveTab] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'game' | 'currency'>('all');
  const [userPurchases] = useState<Purchase[]>([
    { id: 1, product: 'Valorant Points 5000', date: '15.11.2024', amount: 1999 },
    { id: 2, product: 'CS2 Prime Status', date: '10.11.2024', amount: 1299 },
    { id: 3, product: 'Fortnite V-Bucks 2800', date: '05.11.2024', amount: 1499 },
  ]);
  const [referralCode] = useState('ROCKET2024XYZ');
  const [referralEarnings] = useState(2450);

  const filteredProducts = products.filter((product) => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const topProducts = products.filter(p => p.popular).slice(0, 4);
  const discountedProducts = products.filter(p => p.discount).slice(0, 4);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border backdrop-blur-lg bg-background/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="text-3xl">🚀</div>
              <h1 className="text-2xl font-bold text-neon-glow">RocketShop</h1>
            </div>
            
            <nav className="hidden md:flex gap-6">
              <button onClick={() => setActiveTab('home')} className={`text-sm font-medium transition-colors hover:text-primary ${activeTab === 'home' ? 'text-primary' : 'text-foreground/80'}`}>
                Главная
              </button>
              <button onClick={() => setActiveTab('catalog')} className={`text-sm font-medium transition-colors hover:text-primary ${activeTab === 'catalog' ? 'text-primary' : 'text-foreground/80'}`}>
                Каталог
              </button>
              <button onClick={() => setActiveTab('faq')} className={`text-sm font-medium transition-colors hover:text-primary ${activeTab === 'faq' ? 'text-primary' : 'text-foreground/80'}`}>
                FAQ
              </button>
              <button onClick={() => setActiveTab('account')} className={`text-sm font-medium transition-colors hover:text-primary ${activeTab === 'account' ? 'text-primary' : 'text-foreground/80'}`}>
                Личный кабинет
              </button>
            </nav>

            <Button className="bg-primary hover:bg-primary/90 hover-glow">
              <Icon name="ShoppingCart" size={20} />
              <span className="ml-2">Корзина</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {activeTab === 'home' && (
          <div className="space-y-12 animate-slide-up">
            <section className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 p-12 border border-primary/30">
              <div className="relative z-10">
                <Badge className="mb-4 bg-primary text-primary-foreground">Быстрая доставка</Badge>
                <h2 className="text-5xl font-bold mb-4 text-neon-glow">Лучшие игры и валюта</h2>
                <p className="text-xl text-foreground/80 mb-6 max-w-2xl">
                  Мгновенная доставка игровой валюты и игр по выгодным ценам. Гарантия безопасности и поддержка 24/7
                </p>
                <Button size="lg" className="bg-primary hover:bg-primary/90 text-lg hover-glow">
                  <Icon name="Rocket" size={24} />
                  <span className="ml-2">Начать покупки</span>
                </Button>
              </div>
              <div className="absolute top-0 right-0 text-9xl opacity-10">🎮</div>
            </section>

            <section>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-3xl font-bold">🔥 Топ продаж</h3>
                <Button variant="ghost" onClick={() => setActiveTab('catalog')} className="text-primary hover:text-primary/80">
                  Смотреть все
                  <Icon name="ArrowRight" size={18} className="ml-2" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {topProducts.map((product) => (
                  <Card key={product.id} className="group bg-card border-border hover-glow overflow-hidden">
                    <div className="aspect-square bg-muted flex items-center justify-center text-7xl group-hover:scale-110 transition-transform duration-300">
                      {product.image}
                    </div>
                    <div className="p-4">
                      <Badge variant="secondary" className="mb-2">{product.category === 'game' ? 'Игра' : 'Валюта'}</Badge>
                      <h4 className="font-semibold text-lg mb-2">{product.name}</h4>
                      <div className="flex items-center justify-between">
                        <div>
                          {product.discount ? (
                            <>
                              <span className="text-2xl font-bold text-primary">{product.price * (1 - product.discount / 100)}₽</span>
                              <span className="text-sm text-muted-foreground line-through ml-2">{product.price}₽</span>
                            </>
                          ) : (
                            <span className="text-2xl font-bold text-primary">{product.price}₽</span>
                          )}
                        </div>
                        <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                          <Icon name="Plus" size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </section>

            <section>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-3xl font-bold">⚡ Скидки и акции</h3>
                <Button variant="ghost" onClick={() => setActiveTab('catalog')} className="text-primary hover:text-primary/80">
                  Все акции
                  <Icon name="ArrowRight" size={18} className="ml-2" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {discountedProducts.map((product) => (
                  <Card key={product.id} className="group bg-card border-accent/50 hover-glow overflow-hidden relative">
                    <Badge className="absolute top-2 right-2 bg-accent text-accent-foreground z-10 animate-pulse-glow">
                      -{product.discount}%
                    </Badge>
                    <div className="aspect-square bg-muted flex items-center justify-center text-7xl group-hover:scale-110 transition-transform duration-300">
                      {product.image}
                    </div>
                    <div className="p-4">
                      <Badge variant="secondary" className="mb-2">{product.category === 'game' ? 'Игра' : 'Валюта'}</Badge>
                      <h4 className="font-semibold text-lg mb-2">{product.name}</h4>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-2xl font-bold text-accent">{product.price * (1 - (product.discount || 0) / 100)}₽</span>
                          <span className="text-sm text-muted-foreground line-through ml-2">{product.price}₽</span>
                        </div>
                        <Button size="sm" className="bg-accent hover:bg-accent/90">
                          <Icon name="Plus" size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'catalog' && (
          <div className="space-y-6 animate-slide-up">
            <div>
              <h2 className="text-4xl font-bold mb-6">Каталог игр и валюты</h2>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Icon name="Search" size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Поиск игр и валюты..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 bg-card border-border"
                  />
                </div>
                <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as any)} className="w-full md:w-auto">
                  <TabsList className="bg-card border border-border">
                    <TabsTrigger value="all">Все</TabsTrigger>
                    <TabsTrigger value="game">Игры</TabsTrigger>
                    <TabsTrigger value="currency">Валюта</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {filteredProducts.map((product) => (
                <Card key={product.id} className="group bg-card border-border hover-glow overflow-hidden relative">
                  {product.discount && (
                    <Badge className="absolute top-2 right-2 bg-accent text-accent-foreground z-10">
                      -{product.discount}%
                    </Badge>
                  )}
                  {product.popular && (
                    <Badge className="absolute top-2 left-2 bg-primary text-primary-foreground z-10">
                      Популярно
                    </Badge>
                  )}
                  <div className="aspect-square bg-muted flex items-center justify-center text-7xl group-hover:scale-110 transition-transform duration-300">
                    {product.image}
                  </div>
                  <div className="p-4">
                    <Badge variant="secondary" className="mb-2">{product.category === 'game' ? 'Игра' : 'Валюта'}</Badge>
                    <h4 className="font-semibold text-lg mb-2">{product.name}</h4>
                    <div className="flex items-center justify-between">
                      <div>
                        {product.discount ? (
                          <>
                            <span className="text-2xl font-bold text-primary">{product.price * (1 - product.discount / 100)}₽</span>
                            <span className="text-sm text-muted-foreground line-through ml-2">{product.price}₽</span>
                          </>
                        ) : (
                          <span className="text-2xl font-bold text-primary">{product.price}₽</span>
                        )}
                      </div>
                      <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                        <Icon name="ShoppingCart" size={16} />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'faq' && (
          <div className="max-w-3xl mx-auto space-y-6 animate-slide-up">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold mb-4">Часто задаваемые вопросы</h2>
              <p className="text-muted-foreground text-lg">Ответы на популярные вопросы о покупках и доставке</p>
            </div>
            
            <Accordion type="single" collapsible className="space-y-4">
              <AccordionItem value="item-1" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-lg font-semibold hover:text-primary">
                  Как быстро приходит валюта после оплаты?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  Игровая валюта поступает мгновенно в течение 1-5 минут после подтверждения оплаты. В редких случаях доставка может занять до 30 минут.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-2" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-lg font-semibold hover:text-primary">
                  Какие способы оплаты доступны?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  Мы принимаем банковские карты (Visa, MasterCard, МИР), электронные кошельки (ЮMoney, QIWI), СБП и криптовалюту.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-3" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-lg font-semibold hover:text-primary">
                  Безопасно ли покупать игровую валюту?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  Да, абсолютно безопасно. Мы работаем только с официальными методами пополнения и гарантируем безопасность ваших аккаунтов.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-4" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-lg font-semibold hover:text-primary">
                  Можно ли вернуть покупку?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  Возврат цифровых товаров возможен только в случае технических ошибок при доставке. Свяжитесь с поддержкой в течение 24 часов.
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="item-5" className="bg-card border border-border rounded-lg px-6">
                <AccordionTrigger className="text-lg font-semibold hover:text-primary">
                  Как работает реферальная программа?
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  Приглашайте друзей по реферальной ссылке и получайте 5% от их покупок на баланс. Средства можно использовать для новых покупок.
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            <Card className="bg-card border-primary/30 p-8 text-center">
              <Icon name="MessageCircle" size={48} className="mx-auto mb-4 text-primary" />
              <h3 className="text-2xl font-bold mb-2">Не нашли ответ?</h3>
              <p className="text-muted-foreground mb-4">Наша поддержка работает 24/7 и готова помочь вам</p>
              <div className="flex gap-4 justify-center">
                <Button className="bg-secondary hover:bg-secondary/90">
                  <Icon name="Send" size={18} />
                  <span className="ml-2">Telegram</span>
                </Button>
                <Button variant="outline" className="border-primary text-primary hover:bg-primary/10">
                  <Icon name="Mail" size={18} />
                  <span className="ml-2">Email</span>
                </Button>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'account' && (
          <div className="max-w-4xl mx-auto space-y-6 animate-slide-up">
            <div className="text-center mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-primary to-secondary rounded-full mx-auto mb-4 flex items-center justify-center text-4xl">
                👤
              </div>
              <h2 className="text-3xl font-bold">Личный кабинет</h2>
              <p className="text-muted-foreground">Управляйте своими покупками и балансом</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <Card className="bg-gradient-to-br from-primary/20 to-primary/5 border-primary/30 p-6 text-center hover-glow">
                <Icon name="Wallet" size={32} className="mx-auto mb-2 text-primary" />
                <p className="text-sm text-muted-foreground mb-1">Баланс</p>
                <p className="text-3xl font-bold text-primary">2 450₽</p>
              </Card>

              <Card className="bg-gradient-to-br from-secondary/20 to-secondary/5 border-secondary/30 p-6 text-center hover-glow">
                <Icon name="ShoppingBag" size={32} className="mx-auto mb-2 text-secondary" />
                <p className="text-sm text-muted-foreground mb-1">Покупок</p>
                <p className="text-3xl font-bold text-secondary">12</p>
              </Card>

              <Card className="bg-gradient-to-br from-accent/20 to-accent/5 border-accent/30 p-6 text-center hover-glow">
                <Icon name="Users" size={32} className="mx-auto mb-2 text-accent" />
                <p className="text-sm text-muted-foreground mb-1">Рефералов</p>
                <p className="text-3xl font-bold text-accent">8</p>
              </Card>
            </div>

            <Card className="bg-card border-border p-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center">
                <Icon name="History" size={24} className="mr-2 text-primary" />
                История покупок
              </h3>
              <div className="space-y-3">
                {userPurchases.map((purchase) => (
                  <div key={purchase.id} className="flex items-center justify-between p-4 bg-muted rounded-lg hover:bg-muted/80 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
                        <Icon name="Package" size={24} className="text-primary" />
                      </div>
                      <div>
                        <p className="font-semibold">{purchase.product}</p>
                        <p className="text-sm text-muted-foreground">{purchase.date}</p>
                      </div>
                    </div>
                    <p className="text-xl font-bold text-primary">{purchase.amount}₽</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="bg-gradient-to-br from-primary/10 to-secondary/10 border-primary/30 p-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center">
                <Icon name="Gift" size={24} className="mr-2 text-primary" />
                Реферальная программа
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Ваша реферальная ссылка:</p>
                  <div className="flex gap-2">
                    <Input 
                      value={`rocketshop.ru/ref/${referralCode}`} 
                      readOnly 
                      className="bg-background border-border"
                    />
                    <Button className="bg-primary hover:bg-primary/90">
                      <Icon name="Copy" size={18} />
                    </Button>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-background/50 rounded-lg p-4">
                    <p className="text-sm text-muted-foreground mb-1">Заработано с рефералов</p>
                    <p className="text-2xl font-bold text-primary">{referralEarnings}₽</p>
                  </div>
                  <div className="bg-background/50 rounded-lg p-4">
                    <p className="text-sm text-muted-foreground mb-1">Ваш процент</p>
                    <p className="text-2xl font-bold text-secondary">5%</p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  Приглашайте друзей и получайте 5% от каждой их покупки на свой баланс!
                </p>
              </div>
            </Card>
          </div>
        )}
      </main>

      <footer className="border-t border-border mt-16 py-8 bg-card/50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="text-2xl">🚀</div>
                <h3 className="text-xl font-bold">RocketShop</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Лучший магазин игровой валюты с мгновенной доставкой
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Каталог</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-primary cursor-pointer transition-colors">Игры</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Игровая валюта</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Топ продаж</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Скидки</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Информация</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-primary cursor-pointer transition-colors">О компании</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Доставка</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Гарантии</li>
                <li className="hover:text-primary cursor-pointer transition-colors">FAQ</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Связь</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="hover:text-primary cursor-pointer transition-colors">Telegram</li>
                <li className="hover:text-primary cursor-pointer transition-colors">ВКонтакте</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Email</li>
                <li className="hover:text-primary cursor-pointer transition-colors">Поддержка 24/7</li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            © 2024 RocketShop. Все права защищены
          </div>
        </div>
      </footer>
    </div>
  );
}