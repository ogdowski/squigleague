$urls = @(
    'https://wahapedia.ru/aos4/img/battleplans/Passing-Seasons1.png',
    'https://wahapedia.ru/aos4/img/battleplans/Paths-of-the-Fey1.png',
    'https://wahapedia.ru/aos4/img/battleplans/Roiling-Roots1.png',
    'https://wahapedia.ru/aos4/img/battleplans/Cyclic-Shifts.png',
    'https://wahapedia.ru/aos4/img/battleplans/Surge-of-Slaughter.png',
    'https://wahapedia.ru/aos4/img/battleplans/Linked-Ley-Lines.png',
    'https://wahapedia.ru/aos4/img/battleplans/Noxious-Nexus.png',
    'https://wahapedia.ru/aos4/img/battleplans/The-Liferoots1.png',
    'https://wahapedia.ru/aos4/img/battleplans/Bountiful-Equinox.png',
    'https://wahapedia.ru/aos4/img/battleplans/Lifecycle.png',
    'https://wahapedia.ru/aos4/img/battleplans/Creeping-Corruption.png',
    'https://wahapedia.ru/aos4/img/battleplans/Grasp-of-Thorns.png'
)

$names = @(
    'aos-passing-seasons.png',
    'aos-paths-of-the-fey.png',
    'aos-roiling-roots.png',
    'aos-cyclic-shifts.png',
    'aos-surge-of-slaughter.png',
    'aos-linked-ley-lines.png',
    'aos-noxious-nexus.png',
    'aos-the-liferoots.png',
    'aos-bountiful-equinox.png',
    'aos-lifecycle.png',
    'aos-creeping-corruption.png',
    'aos-grasp-of-thorns.png'
)

New-Item -ItemType Directory -Path "assets\battle-plans" -Force | Out-Null

for($i=0; $i -lt $urls.Count; $i++) {
    Invoke-WebRequest -Uri $urls[$i] -OutFile "assets\battle-plans\$($names[$i])" -UseBasicParsing
    Write-Host "Downloaded: $($names[$i])"
}
