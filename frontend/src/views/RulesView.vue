<template>
  <div class="bg-image"></div>
  <div class="container">
    <header>
      <h1 class="text-oldalcim">LopósG Szabályai</h1>
    </header>
    <h3>1. A játék célja</h3>
    <p>A játékosoknak az a céljuk, hogy a játék végére minél több lapot gyűjtsenek össze.</p>

    <h3>2. Játékidő</h3>
    <p>A játék körökre osztott. Minden körben öt lapot kapnak a játékosok. A körök addig ismétlődnek, amíg az összes
      lap el nem fogy a pakliból, vagy a megmaradt lapok már nem oszthatóak egyenlően el.</p>

    <h3>3. Kártyák típusa</h3>
    <p>A játék francia kártyapaklival játszható. Legalább két paklival érdemes játszani, de a játékosok számától
      függően ez növelhető.</p>

    <h3>4. Előkészületek</h3>
    <p>Minden játékos kap öt lapot, amelyet a kezében tart úgy, hogy azt mások ne lássák. Az asztalra egy lapot
      felfordítunk, ez lesz a dobópakli.</p>

    <h3>5. Játékmenet és akciók</h3>
    <ul>
      <li><strong>Lerakás:</strong> Ha a játékosnak van két azonos értékű lapja, lerakhatja azokat az asztalra.</li>
      <li><strong>Dobás:</strong> Egy lapot a dobópaklira helyezhet, ha nincs más akció.</li>
      <li><strong>Lopás:</strong> A játékos a saját lapjával ellophatja egy másik játékos aktív lapjait.</li>
      <!-- <li><strong>Védés:</strong> Lopás esetén a lopás áldozata azonnal, saját körén kívül kivédheti azt egy azonos
        lappal.</li> -->
    </ul>

    <!-- <h3>6. A dobópakli szerepe</h3>
    <p>A dobópakli legfelső lapját a játékosok lopáshoz vagy párképzéshez felhasználhatják. Ha a dobópakli kiürülne,
      új lapot fordítunk fel a pakliból.</p> -->

    <h3>6. Pontozás</h3>
    <p>A játékosok a játék végén a lerakott lapjaik alapján pontokat kapnak:</p>
    <ul>
      <li>2-7 értékű lapok: 5 pont/lap</li>
      <li>8-10 + Bubi, Dáma, Király, Ász: 10 pont/lap</li>
    </ul>

    <h3>7. Győzelem</h3>
    <p>A legtöbb pontot szerző játékos nyer.</p>
  </div>
</template>

<style scoped>
.bg-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://images.unsplash.com/photo-1646809014367-2c267bcba69f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  background-size: cover;
  background-position: center;
  z-index: -1;
}

body {
  background-color: transparent;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
  background-color: #ffffff;
  padding: 2rem;
  margin: 2rem auto;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

header {
  background-color: #4CAF50;
  padding: 1rem;
  text-align: center;
  margin-bottom: 1rem;
  border-radius: 8px 8px 0 0;
}

.text-oldalcim {
  color: #ffffff;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
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