# Rizinova-AI - Full-Stack Next.js + React + Tailwind CSS

## 🚀 Guide de Démarrage

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/Mc-Pentester/Rizinova-AI.git
cd Rizinova-AI
git checkout convert/nextjs-fullstack

# 2. Installer les dépendances
npm install

# 3. Configurer l'environnement
cp .env.example .env.local
# Éditer .env.local avec vos valeurs

# 4. Configurer la base de données
npm run prisma:generate
npm run prisma:migrate

# 5. Démarrer le serveur de développement
npm run dev
```

Accédez à : http://localhost:3000

---

## 📁 Structure du Projet

```
.
├── app/
│   ├── api/                    # Backend API Routes (Next.js)
│   │   ├── auth/              # Authentification
│   │   ├── search/            # Recherche RAG
│   │   ├── knowledge/         # Documents
│   │   ├── health/            # Health check
│   │   └── middleware.ts      # Rate limiting
│   ├── (auth)/                # Pages Auth (login, register)
│   ├── (dashboard)/           # Pages Protégées
│   │   ├── dashboard/
│   │   ├── search/
│   │   └── profile/
│   ├── layout.tsx             # Layout racine
│   ├── page.tsx               # Home page
│   └── error.tsx
├── components/                 # Composants React
│   ├── ui/                    # Composants UI réutilisables
│   ├── layout/                # Layout components
│   ├── forms/                 # Formulaires
│   └── dashboard/             # Dashboard components
├── lib/                        # Utilitaires
│   ├── auth.ts               # Authentification
│   ├── db.ts                 # Client Prisma
│   ├── jwt.ts                # JWT utils
│   ├── rate-limit.ts         # Rate limiting
│   └── api-client.ts         # API client
├── prisma/                     # Prisma schema
│   └── schema.prisma
├── public/                     # Assets statiques
├── types/                      # Types TypeScript
├── styles/                     # CSS global
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

---

## 🔐 Authentification

### JWT avec Session

```typescript
// app/api/auth/login/route.ts
import { generateToken } from '@/lib/jwt'

export async function POST(req: Request) {
  const { email, password } = await req.json()
  
  // Valider les credentials
  const user = await validateUser(email, password)
  
  // Générer JWT token
  const token = generateToken(user.id)
  
  return Response.json({ token, user })
}
```

### Middleware de Protection

```typescript
// lib/auth.ts
export async function protectedRoute(req: Request) {
  const token = req.headers.get('authorization')?.split(' ')[1]
  
  if (!token) {
    return new Response('Unauthorized', { status: 401 })
  }
  
  const user = verifyToken(token)
  return { user }
}
```

---

## 🔍 API Endpoints

### Authentication
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `POST /api/auth/logout` - Se déconnecter
- `GET /api/auth/me` - Profil utilisateur

### Recherche RAG
- `POST /api/search` - Rechercher
- `GET /api/search/:id` - Détails recherche
- `GET /api/search` - Historique

### Documents
- `GET /api/knowledge` - Lister documents
- `POST /api/knowledge` - Créer document
- `PUT /api/knowledge/:id` - Mettre à jour
- `DELETE /api/knowledge/:id` - Supprimer

### Système
- `GET /api/health` - Health check
- `GET /api/stats` - Statistiques

---

## 🎨 Composants Tailwind CSS

### Exemples d'Utilisation

```typescript
// components/ui/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary-600 text-white hover:bg-primary-700',
        outline: 'border border-primary-600 text-primary-600 hover:bg-primary-50',
        ghost: 'hover:bg-gray-100',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2',
        lg: 'px-6 py-3 text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
)
```

---

## 🧪 Tests

```bash
# Lancer les tests
npm test

# Watch mode
npm run test:watch

# Avec couverture
npm test -- --coverage
```

---

## 🚀 Déploiement

### Build

```bash
npm run build
npm start
```

### Vercel (Recommandé)

```bash
npm i -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

---

## 📊 Features

- ✅ **Next.js 14** - Framework React moderne
- ✅ **TypeScript** - Type safety
- ✅ **Tailwind CSS** - Styling moderne
- ✅ **Prisma ORM** - Database management
- ✅ **PostgreSQL** - Base de données robuste
- ✅ **JWT Authentication** - Sécurité
- ✅ **Rate Limiting** - Protection API
- ✅ **SWR** - Data fetching
- ✅ **React Hook Form** - Formulaires
- ✅ **Zod** - Validation
- ✅ **Zustand** - State management

---

## 🔧 Configuration

### Variables d'environnement

Copier `.env.example` en `.env.local` et remplir :

```bash
cp .env.example .env.local
```

### Base de données

```bash
# Générer Prisma client
npm run prisma:generate

# Créer migrations
npm run prisma:migrate

# Ouvrir Prisma Studio
npm run prisma:studio
```

---

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Prisma Docs](https://www.prisma.io/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)

---

## 📝 License

MIT License

---

**Version:** 2.0.0 (Next.js Full-Stack)
**Date:** 3 juin 2026
**Branche:** `convert/nextjs-fullstack`
