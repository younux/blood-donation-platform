/**
 * Created by younes.benhoumich on 05/09/2017.
 */

const APP_API_URL = ' http://localhost/server/api/';

export const apiInjectables: Array<any> = [
  {provide: 'APP_API_URL', useValue: APP_API_URL},
]