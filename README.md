# Oba.az Qiymət API

## Railway-ə Deploy (Pulsuz)

### 1. GitHub-a yüklə
```bash
git init
git add .
git commit -m "ilk commit"
git branch -M main
git remote add origin https://github.com/SENIN_ADIN/oba-backend.git
git push -u origin main
```

### 2. Railway-də deploy et
1. https://railway.app saytına keç (GitHub ilə qeydiyyat)
2. "New Project" → "Deploy from GitHub repo" seç
3. Bu repo-nu seç
4. Deploy avtomatik başlayır (3-5 dəq)
5. "Settings" → "Networking" → "Generate Domain" basın
6. Sənin URL-in hazır olur: `https://oba-backend-xxx.railway.app`

### 3. Test et
```
https://SENIN_URL.railway.app/search?q=ananas+suyu
```

## API İstifadəsi

### Axtarış
```
GET /search?q=MƏHSUL_ADI
```

### Cavab formatı
```json
{
  "query": "ananas suyu",
  "count": 3,
  "results": [
    {
      "name": "Moi Ananas Suyu 1L",
      "price": "1.89",
      "image": "https://...",
      "url": "https://oba.az/..."
    }
  ]
}
```
