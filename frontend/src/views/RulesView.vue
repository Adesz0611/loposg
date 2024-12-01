<template>
  <div class="container">
  <header>
    <h1>LopósG Szabályai</h1>
  </header>
  <h2>1. A játék célja</h2>
  <p>A játékosoknak az a céljuk, hogy a játék végére minél több lapot gyűjtsenek össze.</p>

  <h2>2. Játékidő</h2>
  <p>A játék körökre osztott. Minden körben öt lapot kapnak a játékosok. A körök addig ismétlődnek, amíg az összes
    lap el nem fogy a pakliból, vagy a megmaradt lapok már nem oszthatóak egyenlően el.</p>

  <h2>3. Kártyák típusa</h2>
  <p>A játék francia kártyapaklival játszható. Legalább két paklival érdemes játszani, de a játékosok számától
    függően ez növelhető.</p>

  <h2>4. Előkészületek</h2>
  <p>Minden játékos kap öt lapot, amelyet a kezében tart úgy, hogy azt mások ne lássák. Az asztalra egy lapot
    felfordítunk, ez lesz a dobópakli.</p>

  <h2>5. Játékmenet és akciók</h2>
  <ul>
    <li><strong>Lerakás:</strong> Ha a játékosnak van két azonos értékű lapja, lerakhatja azokat az asztalra.</li>
    <li><strong>Dobás:</strong> Egy lapot a dobópaklira helyezhet, ha nincs más akció.</li>
    <li><strong>Lopás:</strong> A játékos a saját lapjával ellophatja egy másik játékos aktív lapjait.</li>
    <li><strong>Védés:</strong> Lopás esetén a lopás áldozata azonnal, saját körén kívül kivédheti azt egy azonos
      lappal.</li>
  </ul>

  <h2>6. A dobópakli szerepe</h2>
  <p>A dobópakli legfelső lapját a játékosok lopáshoz vagy párképzéshez felhasználhatják. Ha a dobópakli kiürülne,
    új lapot fordítunk fel a pakliból.</p>

  <h2>7. Pontozás</h2>
  <p>A játékosok a játék végén a lerakott lapjaik alapján pontokat kapnak:</p>
  <ul>
    <li>2-7 értékű lapok: 5 pont/lap</li>
    <li>8-10 + Bubi, Dáma, Király, Ász: 10 pont/lap</li>
  </ul>

  <h2>8. Győzelem</h2>
  <p>A legtöbb pontot szerző játékos nyer.</p>
  </div>
</template>

<style>
body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  background-color: #f8f9fa;
  color: #333;
  margin: 0;
  padding: 0;
}

header {
  color: white;
  text-align: center;
  padding: 1rem;
}

main {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1,
h2 {
  color: #007bff;
}

ul {
  padding-left: 1.5rem;
}

footer {
  text-align: center;
  padding: 1rem;
  background: #f1f1f1;
  margin-top: 2rem;
}
</style>