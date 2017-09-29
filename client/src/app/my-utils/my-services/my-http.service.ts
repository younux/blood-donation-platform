import { Injectable } from '@angular/core';
import {
  Http, Request, RequestOptions, RequestOptionsArgs, Response, Headers,
  XHRBackend
} from "@angular/http";
import {Observable} from "rxjs/Observable";
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import {Router} from "@angular/router";
import {AuthenticationService} from "./authentication.service";


@Injectable()
export class MyHttpService extends Http {
  private config: InterceptorConfig;

  constructor(backend: XHRBackend,
              defaultOptions: RequestOptions,
              private router: Router,
              private authenticationService: AuthenticationService) {
    super(backend, defaultOptions);
    this.config = new InterceptorConfig();
  }

  request(url: string | Request, options?: RequestOptionsArgs): Observable<Response> {
    const jwtToken: string = this.getToken();
    if (jwtToken) {
      if (typeof url === 'string') { // meaning we have to add the token to the options, not in url
        if (!options) {
          // let's make option object
          options = {headers: new Headers()};
        }
        options.headers.set(this.config.headerName, this.config.headerPrefix + ' ' + jwtToken);

      } else {
        // we have to add the token to the url object
        url.headers.set(this.config.headerName, this.config.headerPrefix + ' ' + jwtToken);
      }
    }

    return super.request(url, options);
  }

  get(url: string, options?: RequestOptionsArgs): Observable<Response> {
    return this.intercept(super.get(url, this.getRequestOptionArgs(options)));
  }

  post(url: string, body: any, options?: RequestOptionsArgs, noIntercept?: boolean): Observable<Response> {
    return this.intercept(super.post(url, body, this.getRequestOptionArgs(options)));
  }

  put(url: string, body: any, options?: RequestOptionsArgs, noIntercept?: boolean): Observable<Response> {
    return this.intercept(super.put(url, body, this.getRequestOptionArgs(options)));

  }

  delete(url: string, options?: RequestOptionsArgs, noIntercept?: boolean): Observable<Response> {
    return this.intercept(super.delete(url, options));
  }

  private intercept(observable: Observable<Response>): Observable<Response> {
    return observable
      .map( response => {
        const authHeader = response.headers.get('Authorization');
        if (authHeader) {
          // store jwt token in local storage
          this.authenticationService.setToken(authHeader.split(' ')[1]);
        }
      return response;
      })
      .catch(err => {
        // Check if we have Unauthorised request
        if (err.status === 401) {
          console.log("MyHttpService : Unauthorised : no token or session expired");
          if (err.json().detail) {
            // Check if the session has expired
            if (err.json().detail === "Signature has expired.") {
              console.log("MyHttpService : session expired");
              // Redirect to login screen
              this.router.navigate(['/profiles', 'login']);
            }
          }
        }
        return Observable.throw(err);
      });

  }

  private getRequestOptionArgs(options?: RequestOptionsArgs): RequestOptionsArgs {
    if (options == null) {
      options = new RequestOptions();
    }
    if (options.headers == null) {
      options.headers = new Headers();
    }
    options.headers.append('Content-Type', 'application/json');
    return options;
  }

  protected getToken(): string {
    // Check if the user is authenticated
    if (this.authenticationService.isAuthenticatedValue()) {
      return this.authenticationService.getToken();
    }else {
      return null;
    }
  }

  // protected refreshToken(): Observable<Response> {
  //
  // }


}


export interface InterceptorConfigOptional {
  headerName?: string;
  headerPrefix?: string;
}

const DEFAULT_HEADER_NAME = 'Authorization';
const DEFAULT_HEADER_PREFIX = 'JWT';

export class InterceptorConfig {

  headerName: string = DEFAULT_HEADER_NAME;
  headerPrefix: string = DEFAULT_HEADER_PREFIX;

  constructor(config?: InterceptorConfigOptional) {
    config = config || {};
    Object.assign(this, config);
  }
}

export function myHttpServiceFactory(backend: XHRBackend,
                                     options: RequestOptions,
                                     router: Router,
                                     authenticationService: AuthenticationService) {
  return new MyHttpService(backend, options, router, authenticationService);
 }