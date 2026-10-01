import { expect, test } from '@playwright/test';

test('permite ingresar, crear una actividad y reprogramarla', async ({ page }) => {
  let activities: Array<Record<string, unknown>> = [];
  let patchCalled = false;

  await page.route('**/api/auth/token/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ access: 'access-token', refresh: 'refresh-token' }),
    });
  });
  await page.route('**/api/asociados/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 7, nombre: 'Ana', apellidos: 'Pérez', email: 'ana@example.com' }]),
    });
  });
  await page.route('**/api/actividades/**', async (route) => {
    const request = route.request();
    if (request.method() === 'POST') {
      const payload = request.postDataJSON() as Record<string, unknown>;
      const created = {
        id: '1',
        tipo: payload.tipo,
        descripcion: payload.descripcion ?? '',
        fecha_inicio: payload.fecha_inicio,
        fecha_fin: payload.fecha_fin,
        asociado: payload.asociado,
      };
      activities = [created];
      await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(created) });
      return;
    }
    if (request.method() === 'PATCH') {
      patchCalled = true;
      const payload = request.postDataJSON() as Record<string, unknown>;
      activities = activities.map((activity) => ({ ...activity, fecha_inicio: payload.fecha_inicio, fecha_fin: payload.fecha_fin }));
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(activities[0]) });
      return;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(activities) });
  });

  await page.goto('/');
  await page.getByLabel('Correo electrónico de acceso').fill('admin@example.com');
  await page.getByLabel('Contraseña de acceso').fill('Password123');
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();
  await expect(page.getByRole('heading', { name: 'Actividades' })).toBeVisible();

  await page.getByRole('button', { name: 'Crear actividad' }).click();
  await page.getByLabel('Título').fill('Visita de cliente');
  await page.getByLabel('Asociado').selectOption('7');
  await page.getByRole('button', { name: 'Guardar' }).click();
  await expect(page.getByText('Visita de cliente')).toBeVisible();

  const card = page.locator('.activity-card').filter({ hasText: 'Visita de cliente' });
  const targetDay = page.locator('.calendar-day').nth(10);
  await card.dragTo(targetDay);
  await expect.poll(() => patchCalled).toBeTruthy();
});
